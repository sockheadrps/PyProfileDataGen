from github import Github
from dotenv import load_dotenv
import os
import json
import re
from collections import defaultdict
import pandas as pd
import configparser
from datetime import datetime, timedelta, timezone
from pytz import timezone as tz


# Load environment variables
load_dotenv()

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")
DEBUG = config.getboolean("Debug", "debug")
STEP_COUNT = config.getint("Debug", "step_count")
ACCESS_TOKEN = os.getenv("TOKEN")
USER = config.get("Settings", "github_user_name")
TIMEZONE = config.get("Settings", "target_tz")
target_tz = tz(TIMEZONE)
print(USER)

# Initialize GitHub API
g = Github(ACCESS_TOKEN)
user = g.get_user(USER)


def count_lines(content):
    return len(content.splitlines())


def count_python_constructs(content):
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

    # Patterns for functions
    async_function_pattern = r"async\s+def\s+\w+\b"
    function_pattern = r"\bdef\s+\w+\b"

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

        # Count async functions first
        async_functions = len(re.findall(async_function_pattern, line))
        counts["async functions created"] += async_functions

        # Count all functions
        all_functions = len(re.findall(function_pattern, line))
        counts["regular functions created"] += all_functions - async_functions

        counts["classes created"] += len(re.findall(r"\bclass\b", line))

    return libraries, counts


def is_recent_commit(commit_date):
    return commit_date >= datetime.now(timezone.utc) - timedelta(days=90)


# Initialize data structure
repo_data = {"repo_stats": [], "commit_counts": {},
             "construct_counts": [], "recent_commits": []}

commit_messages = defaultdict(list)
commit_times = []

repo_iter = iter(user.get_repos())
for i, repo in enumerate(repo_iter):
    if not repo.fork and not repo.archived:
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

        # Skip repos that are not owned by the user
        if repo.owner.login != user.login:
            continue

        print(f"Processing {repo.name}...")
        commits = repo.get_commits()
        total_commits = 0
        recent_commits = []
        for commit in commits:
            commit_date = commit.commit.author.date
            commit_times.append([commit_date.weekday(), commit_date.hour])
            commit_messages[repo.name].append(commit.commit.message)
            total_commits += 1

            if is_recent_commit(commit_date):
                commit_details = {
                    "repo_name": repo.name,
                    "repo_url": f"https://github.com/{user.login}/{repo.name}",
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit_date.isoformat()
                }

                commit_data = repo.get_commit(commit.sha)
                commit_details["additions"] = commit_data.stats.additions
                commit_details["deletions"] = commit_data.stats.deletions
                commit_details["total_changes"] = commit_data.stats.total

                recent_commits.append(commit_details)

        repo_info = {
            "repo_name": repo.name,
            "python_files": [],
            "libraries": set(),
            "total_python_files": 0,
            "total_python_lines": 0,
            "file_extensions": {},
            "total_commits": total_commits,
            "commit_messages": commit_messages[repo.name],
            "construct_counts": {
                "if statements": 0,
                "while loops": 0,
                "for loops": 0,
                "regular functions created": 0,
                "async functions created": 0,
                "classes created": 0,
            },
        }

        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                # Split on dot to handle special cases
                split_path = file_content.path.rsplit('.', 1)
                if len(split_path) > 1:
                    file_extension = '.' + split_path[-1]
                else:
                    file_extension = file_content.path

                if file_extension in repo_info["file_extensions"]:
                    repo_info["file_extensions"][file_extension] += 1
                else:
                    repo_info["file_extensions"][file_extension] = 1

                if file_extension == ".py":
                    repo_info["total_python_files"] += 1
                    if file_content.encoding == "base64":
                        try:
                            file_content_data = file_content.decoded_content.decode(
                                "utf-8")
                            repo_info["python_files"].append(file_content.path)
                            repo_info["total_python_lines"] += count_lines(
                                file_content_data)
                            libs, construct_counts = count_python_constructs(
                                file_content_data)
                            repo_info["libraries"].update(libs)

                            for key in repo_info["construct_counts"]:
                                repo_info["construct_counts"][key] += construct_counts[key]

                        except UnicodeDecodeError:
                            print(
                                f"Skipping non-UTF-8 file: {file_content.path}")
                    else:
                        print(
                            f"Skipping file with unsupported encoding: {file_content.path}")

        repo_info["libraries"] = list(repo_info["libraries"])
        repo_data["repo_stats"].append(repo_info)
        repo_data["recent_commits"].extend(recent_commits)

# Create DataFrame for commit times
commit_df = pd.DataFrame(commit_times, columns=["DayOfWeek", "HourOfDay"])

# Verify that 'HourOfDay' and 'DayOfWeek' are correctly created
print(commit_df.head())
print(commit_df.columns)

# Ensure 'HourOfDay' exists and has values
if 'HourOfDay' not in commit_df.columns:
    raise KeyError("The 'HourOfDay' column is missing from the DataFrame!")

# Map weekdays to names
weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
               3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
commit_df["DayOfWeek"] = commit_df["DayOfWeek"].map(weekday_map)

# Group commit data by day and hour, and count the occurrences
commit_counts = commit_df.groupby(
    ["DayOfWeek", "HourOfDay"]).size().reset_index(name="Count")

# Verify that the grouped DataFrame is correctly structured
print(commit_counts.head())

# Build the commit counts dictionary
commit_counts_dict = {}
for _, row in commit_counts.iterrows():
    day = row["DayOfWeek"]
    hour = row["HourOfDay"]
    count = row["Count"]
    if day not in commit_counts_dict:
        commit_counts_dict[day] = {}
    commit_counts_dict[day][hour] = count

# Assign the dictionary to repo_data
repo_data["commit_counts"] = commit_counts_dict

if DEBUG:
    print(f"Debug information: {repo_data}")

# Write data to JSON file
with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)
