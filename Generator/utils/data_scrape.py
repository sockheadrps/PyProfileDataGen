from github import Github
from dotenv import load_dotenv
import os
import json
import re
from collections import defaultdict
import pandas as pd
import configparser

load_dotenv()

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Debug settings
DEBUG = config.getboolean("Debug", "debug")
STEP_COUNT = config.getint("Debug", "step_count")

ACCESS_TOKEN = os.getenv("TOKEN")
g = Github(ACCESS_TOKEN)
user = g.get_user()


def count_lines(content):
    return len(content.splitlines())


def count_python_constructs(content):
    counts = {
        "if statements": 0,
        "while loops": 0,
        "for loops": 0,
        "functions created": 0,
        "async functions created": 0,
        "classes created": 0,
    }
    check_imports = True
    importless_streak = 0
    libraries = set()
    import_patterns = [r"^import\s+(\w+)", r"^from\s+(\w+)\s+import"]

    for line in content.splitlines():
        if check_imports:
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    libraries.add(match.group(1))
                    importless_streak = 0
                else:
                    importless_streak += 1
            if importless_streak > 10:
                check_imports = False

        counts["if statements"] += len(re.findall(r"\bif\b", line))
        counts["while loops"] += len(re.findall(r"\bwhile\b", line))
        counts["for loops"] += len(re.findall(r"\bfor\b", line))
        counts["functions created"] += len(re.findall(r"\bdef\b", line))
        counts["async functions created"] += len(re.findall(r"\basync\s+def\b", line))
        counts["classes created"] += len(re.findall(r"\bclass\b", line))

    return libraries, counts


repo_data = {"repo_stats": [], "commit_counts": [], "construct_counts": []}

commit_messages = defaultdict(list)
commit_times = []

# Limit the number of repositories processed based on SCRAP_COUNT
repo_iter = iter(user.get_repos())
for i, repo in enumerate(repo_iter):
    if not repo.fork:
        if DEBUG:
            if i >= STEP_COUNT:
                break
        
        # Skip profile repo
        if not config.getboolean("Settings", "include_profile_repo"):
            if repo.name == user.login:
                continue
        
        # Skip ignored repos
        if repo.name in config.get("Settings", "ignored_repos"):
            continue

        print(f"Processing {repo.name}...")
        commits = repo.get_commits()
        total_commits = 0
        for commit in commits:
            commit_date = commit.commit.author.date
            commit_times.append([commit_date.weekday(), commit_date.hour])
            commit_messages[repo.name].append(commit.commit.message)
            total_commits += 1

        repo_info = {
            "repo_name": repo.name,
            "python_files": [],
            "libraries": set(),
            "total_python_lines": 0,
            "file_extensions": {},
            "total_commits": total_commits,
            "commit_messages": commit_messages[repo.name],
            "construct_counts": {},
        }

        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file_extension = os.path.splitext(file_content.path)[1]

                if file_extension in repo_info["file_extensions"]:
                    repo_info["file_extensions"][file_extension] += 1
                else:
                    repo_info["file_extensions"][file_extension] = 1

                if file_extension == ".py":
                    if file_content.encoding == "base64":
                        try:
                            file_content_data = file_content.decoded_content.decode("utf-8")
                            repo_info["python_files"].append(file_content.path)
                            repo_info["total_python_lines"] += count_lines(file_content_data)
                            libs, construct_counts = count_python_constructs(file_content_data)
                            repo_info["libraries"].update(libs)
                            repo_info["construct_counts"] = construct_counts
                        except UnicodeDecodeError:
                            print(f"Skipping non-UTF-8 file: {file_content.path}")
                    else:
                        print(f"Skipping file with unsupported encoding: {file_content.path}")

        repo_info["libraries"] = list(repo_info["libraries"])
        repo_data["repo_stats"].append(repo_info)

commit_df = pd.DataFrame(commit_times, columns=["DayOfWeek", "HourOfDay"])

weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
commit_df["DayOfWeek"] = commit_df["DayOfWeek"].map(weekday_map)

commit_counts = commit_df.groupby(["DayOfWeek", "HourOfDay"]).size().reset_index(name="Count")

repo_data["commit_counts"] = commit_counts.to_dict(orient="records")

if DEBUG:
    print(f"Commit counts:\n{commit_counts}")

with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)
