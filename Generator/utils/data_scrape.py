from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv
import os, json, re
from collections import defaultdict
import pandas as pd
import configparser
from datetime import datetime, timedelta, timezone
from pytz import timezone as tz
import time


# ===== Env & Config =====
load_dotenv()
config = configparser.ConfigParser()
config.read("config.ini")

DEBUG = config.getboolean("Debug", "debug", fallback=False)
STEP_COUNT = config.getint("Debug", "step_count", fallback=10)
ACCESS_TOKEN = os.getenv("TOKEN")
USER = config.get("Settings", "github_user_name")
TIMEZONE = config.get("Settings", "target_tz", fallback="America/New_York")
target_tz = tz(TIMEZONE)
IGNORED = {
    r.strip()
    for r in config.get("Settings", "ignored_repos", fallback="").split(",")
    if r.strip()
}

# Resume behavior
OUTPUT_PATH = "repo_data.json"
OVERWRITE_EXISTING = config.getboolean("Debug", "overwrite_existing", fallback=True)  # set True to reprocess repos even if they exist in the JSON

# Directories to exclude from processing (common build/cache dirs)
EXCLUDE_DIRS = {
    ".venv/", "venv/", "env/", "__pycache__/", ".mypy_cache/", ".pytest_cache/",
    ".github/", ".git/", "build/", "dist/", "site-packages/", "node_modules/",
    ".idea/", ".vscode/", ".ruff_cache/", ".tox/", ".eggs/"
}

print(USER)

# ===== Helpers =====

def wait_for_rate_limit(github_client):
    """Block until we have at least 1 core call remaining.
    Uses Github.rate_limiting and rate_limiting_resettime, which work across PyGithub versions.
    """
    while True:
        remaining, _limit = github_client.rate_limiting  # (remaining, limit)
        if remaining > 0:
            return
        reset_epoch = github_client.rate_limiting_resettime  # unix seconds
        sleep_sec = max(5, int(reset_epoch - time.time()) + 1)
        print(f"⏳ Waiting for GitHub rate limit reset in ~{sleep_sec}s…")
        time.sleep(sleep_sec)

def preflight(github_client, floor=5):
    """Ensure we have a small headroom before entering a heavy loop."""
    remaining, _limit = github_client.rate_limining if hasattr(github_client, "rate_limining") else github_client.rate_limiting
    if remaining < floor:
        print("⏰ Low remaining calls, waiting for reset…")
        wait_for_rate_limit(github_client)

def safe_github_call(fn, *args, **kwargs):
    while True:
        try:
            return fn(*args, **kwargs)
        except GithubException as e:
            msg = str(e).lower()
            if e.status == 403 and "rate limit" in msg:
                print("⏰ Rate limit hit. Waiting for reset...")
                wait_for_rate_limit(g)
                continue
            raise

def count_lines(content: str) -> int:
    return len(content.splitlines())

def count_python_constructs(content: str):
    counts = {
        "if statements": 0,
        "while loops": 0,
        "for loops": 0,
        "regular functions created": 0,
        "async functions created": 0,
        "classes created": 0,
    }
    check_imports = True
    importless_streak = 0
    libraries = set()
    import_patterns = [r"^import\s+(\w+)", r"^from\s+(\w+)\s+import"]
    async_function_pattern = r"(?<!\w)async\s+def\s+\w+\b"
    function_pattern = r"(?<!\w)def\s+\w+\b"

    for line in content.splitlines():
        if check_imports:
            matched = False
            for pattern in import_patterns:
                m = re.match(pattern, line)
                if m:
                    libraries.add(m.group(1))
                    matched = True
                    break
            if matched:
                importless_streak = 0
            else:
                importless_streak += 1
                if importless_streak > 10:
                    check_imports = False

        counts["if statements"] += len(re.findall(r"\bif\b", line))
        counts["while loops"] += len(re.findall(r"\bwhile\b", line))
        counts["for loops"] += len(re.findall(r"\bfor\b", line))
        async_functions = len(re.findall(async_function_pattern, line))
        all_functions = len(re.findall(function_pattern, line))
        counts["async functions created"] += async_functions
        counts["regular functions created"] += max(0, all_functions - async_functions)
        counts["classes created"] += len(re.findall(r"(?<!\w)class\b", line))

    return libraries, counts

def is_recent_commit(commit_date):
    return commit_date >= datetime.now(timezone.utc) - timedelta(days=90)

def load_existing(path):
    if not os.path.exists(path):
        return {
            "repo_stats": [],
            "commit_counts": {},
            "construct_counts": [],
            "recent_commits": []
        }
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # Corrupted? Start fresh but keep a backup
            os.replace(path, path + ".corrupt_backup")
            return {
                "repo_stats": [],
                "commit_counts": {},
                "construct_counts": [],
                "recent_commits": []
            }
    # Normalize fields expected by this version
    data.setdefault("repo_stats", [])
    data.setdefault("commit_counts", {})
    data.setdefault("construct_counts", [])
    data.setdefault("recent_commits", [])
    return data

def atomic_save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, path)

def rebuild_commit_counts_from_repo_stats(repo_stats):
    # Aggregate all per-repo commit_times into a dataframe and rebuild the heatmap
    rows = []
    for r in repo_stats:
        for d, h in r.get("commit_times", []):
            rows.append((d, h))
    if not rows:
        return {}
    df = pd.DataFrame(rows, columns=["DayOfWeek", "HourOfDay"])
    weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
                   3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    df["DayOfWeek"] = df["DayOfWeek"].map(weekday_map)
    commit_counts = df.groupby(["DayOfWeek", "HourOfDay"]).size().reset_index(name="Count")
    out = {}
    for _, row in commit_counts.iterrows():
        day = row["DayOfWeek"]
        hour = int(row["HourOfDay"])
        count = int(row["Count"])
        out.setdefault(day, {})[hour] = count
    return out

# ===== Init GitHub =====
if not ACCESS_TOKEN:
    raise RuntimeError("TOKEN env var is empty. Authenticated requests are required to avoid 60/hr limit.")

g = Github(ACCESS_TOKEN, per_page=100)
wait_for_rate_limit(g)
user = safe_github_call(g.get_user, USER)

# ===== Load prior progress (resume-safe) =====
repo_data = load_existing(OUTPUT_PATH)

# Map of repo_name -> index in repo_stats (for fast replace if overwriting)
name_to_index = {r.get("repo_name"): idx for idx, r in enumerate(repo_data["repo_stats"])}

processed_count = 0

# ===== Iterate repos =====
repo_iter = safe_github_call(user.get_repos)
for i, repo in enumerate(repo_iter):
    if DEBUG and i >= STEP_COUNT:
        print(f"🔍 Debug mode: stopping after {STEP_COUNT} repositories")
        break

    if repo.archived:
        continue
    if not config.getboolean("Settings", "include_profile_repo", fallback=False) and repo.name == user.login:
        continue
    if repo.name in IGNORED:
        continue
    if repo.owner.login != user.login:
        continue

    # Skip if already processed (unless overwrite)
    if not OVERWRITE_EXISTING and repo.name in name_to_index:
        print(f"↩️  Skipping already-processed repo: {repo.name}")
        continue

    # Fork provenance check
    if repo.fork:
        try:
            source_repo = repo.source
            if source_repo and source_repo.owner.login != user.login:
                print(f"⏭️ Skipping fork of {source_repo.owner.login}/{source_repo.name}")
                continue
        except GithubException as e:
            print(f"⚠️ Could not determine source of fork {repo.name}: {e}")
            continue

    print(f"Processing {repo.name}...")
    total_commits = 0
    recent_commits = []
    per_repo_commit_times = []  # (weekday_int, hour_int)

    # ===== Commits (ALL history) =====
    try:
        preflight(g)
        commits = safe_github_call(repo.get_commits)  # <-- no 'since': all time
        for commit in commits:
            author = getattr(commit.commit, "author", None)
            if not author or not author.date:
                continue
            commit_date = author.date.replace(tzinfo=timezone.utc).astimezone(target_tz)
            per_repo_commit_times.append([commit_date.weekday(), commit_date.hour])
            total_commits += 1

            if is_recent_commit(commit_date):
                try:
                    details = {
                        "repo_name": repo.name,
                        "repo_url": f"https://github.com/{user.login}/{repo.name}",
                        "sha": commit.sha,
                        "message": commit.commit.message or "",
                        "author": author.name if author else None,
                        "date": commit_date.isoformat()
                    }
                    preflight(g)
                    commit_data = safe_github_call(repo.get_commit, commit.sha)
                    stats = getattr(commit_data, "stats", None)
                    if stats:
                        details["additions"] = stats.additions
                        details["deletions"] = stats.deletions
                        details["total_changes"] = stats.total
                    recent_commits.append(details)
                except GithubException as e:
                    print(f"⚠️ Error getting commit details for {commit.sha}: {e}")
                    continue
    except GithubException as e:
        if e.status == 409 and "Git Repository is empty" in str(e):
            print(f"⚠️ Skipping empty repository: {repo.name}")
            continue
        elif e.status == 404:
            print(f"⚠️ Repository not found or inaccessible: {repo.name}")
            continue
        else:
            print(f"❌ Error processing commits for {repo.name}: {e}")
            continue

    # ===== Repo info & contents =====
    repo_info = {
        "repo_name": repo.name,
        "python_files": [],
        "libraries": set(),
        "total_python_files": 0,
        "total_python_lines": 0,
        "file_extensions": {},
        "total_commits": total_commits,
        "commit_messages": [],  # optional to keep; you can fill similarly to earlier if needed
        "commit_times": per_repo_commit_times,  # <-- stored for resume heatmap
        "construct_counts": {
            "if statements": 0,
            "while loops": 0,
            "for loops": 0,
            "regular functions created": 0,
            "async functions created": 0,
            "classes created": 0,
        },
    }

    # OPTIONAL: collect commit messages too (commented to save calls/time)
    # If you want them, uncomment the msg append above when iterating commits.

    try:
        preflight(g)
        contents = list(safe_github_call(repo.get_contents, ""))
        processed_files = set()  # Track processed files to avoid duplicates
        
        while contents:
            file_content = contents.pop(0)
            
            # Skip if we've already processed this file
            if file_content.path in processed_files:
                continue
                
            if file_content.type == "dir":
                # Skip excluded directories and hidden directories
                if (file_content.path.startswith('.') or 
                    any(excluded in file_content.path for excluded in EXCLUDE_DIRS)):
                    continue
                    
                try:
                    preflight(g)
                    new_contents = safe_github_call(repo.get_contents, file_content.path)
                    # Only add files we haven't seen
                    for new_file in new_contents:
                        if new_file.path not in processed_files:
                            contents.append(new_file)
                except GithubException as e:
                    if e.status == 404:
                        print(f"⚠️ Directory not found: {file_content.path}")
                        continue
                    else:
                        print(f"⚠️ Skipping directory on error: {file_content.path} ({e})")
                        continue
            else:
                # Mark this file as processed
                processed_files.add(file_content.path)
                
                split_path = file_content.path.rsplit('.', 1)
                file_extension = '.' + split_path[-1] if len(split_path) > 1 else file_content.path
                repo_info["file_extensions"][file_extension] = repo_info["file_extensions"].get(file_extension, 0) + 1

                if file_extension == ".py":
                    repo_info["total_python_files"] += 1
                    try:
                        raw = getattr(file_content, "decoded_content", None)
                        if raw is None:
                            preflight(g)
                            refetched = safe_github_call(repo.get_contents, file_content.path)
                            raw = getattr(refetched, "decoded_content", None)
                        if raw is None:
                            print(f"⚠️ Could not read {file_content.path}, skipping")
                            continue

                        # Check if this is actually a text file
                        if raw and len(raw) > 0:
                            try:
                                text = raw.decode("utf-8", errors="strict")
                                
                                # Only count if it's actually Python code (not just a .py file)
                                if text.strip() and not text.startswith(b'\x00'.decode()):  # Check for binary
                                    repo_info["python_files"].append(file_content.path)
                                    line_count = count_lines(text)
                                    repo_info["total_python_lines"] += line_count
                                    print(f"  📄 {file_content.path}: {line_count} lines")
                                    
                                    # Also show running total for this repo
                                    print(f"    Running total: {repo_info['total_python_lines']} lines in {repo_info['total_python_files']} files")
                                    
                                    libs, construct_counts = count_python_constructs(text)
                                    repo_info["libraries"].update(libs)
                                    for k, v in construct_counts.items():
                                        repo_info["construct_counts"][k] += v
                                else:
                                    print(f"  ⚠️ Skipping binary/empty file: {file_content.path}")
                                    
                            except UnicodeDecodeError:
                                print(f"  ⚠️ Skipping non-UTF-8 file: {file_content.path}")
                        else:
                            print(f"  ⚠️ Skipping empty file: {file_content.path}")
                            
                    except GithubException as e:
                        msg = str(e).lower()
                        if e.status == 403 and "rate limit" in msg:
                            print(f"⏰ Rate limit while reading {file_content.path}. Waiting…")
                            wait_for_rate_limit(g)
                            # Don't retry - just skip to avoid double counting
                            continue
                        else:
                            print(f"⚠️ Error reading file {file_content.path}: {e}")
                            continue
    except GithubException as e:
        print(f"❌ Error processing repository {repo.name}: {e}")
        continue

    repo_info["libraries"] = list(repo_info["libraries"])

    # Merge into repo_data (replace or append)
    if repo.name in name_to_index and OVERWRITE_EXISTING:
        repo_data["repo_stats"][name_to_index[repo.name]] = repo_info
    elif repo.name in name_to_index and not OVERWRITE_EXISTING:
        # Skip because we already processed in a previous run
        pass
    else:
        repo_data["repo_stats"].append(repo_info)
        name_to_index[repo.name] = len(repo_data["repo_stats"]) - 1

    # Merge recent commits
    repo_data["recent_commits"].extend(recent_commits)

    # Rebuild heatmap from ALL per-repo commit_times so far (cheap)
    repo_data["commit_counts"] = rebuild_commit_counts_from_repo_stats(repo_data["repo_stats"])

    # Checkpoint after each repo (atomic)
    atomic_save(OUTPUT_PATH, repo_data)
    processed_count += 1
    print(f"💾 Saved progress after {repo.name} ({processed_count} repos this run)")
    print(f"  📊 FINAL REPO SUMMARY:")
    print(f"     Python files: {repo_info['total_python_files']}")
    print(f"     Total lines: {repo_info['total_python_lines']}")
    if repo_info['total_python_files'] > 0:
        print(f"     Average lines per file: {repo_info['total_python_lines'] / repo_info['total_python_files']:.1f}")
    print(f"     Files processed:")
    for py_file in repo_info['python_files']:
        print(f"       - {py_file}")
    print()

print("✅ Done. Final data saved to repo_data.json")

# Print final summary
total_python_files = sum(repo.get("total_python_files", 0) for repo in repo_data["repo_stats"])
total_python_lines = sum(repo.get("total_python_lines", 0) for repo in repo_data["repo_stats"])
print(f"\n📊 FINAL SUMMARY:")
print(f"   Total repositories: {len(repo_data['repo_stats'])}")
print(f"   Total Python files: {total_python_files}")
print(f"   Total Python lines: {total_python_lines}")
print(f"   Average lines per file: {total_python_lines / total_python_files if total_python_files > 0 else 0:.1f}")
