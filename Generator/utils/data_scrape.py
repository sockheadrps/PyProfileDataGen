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

# Load environment variables from a .env file
load_dotenv()

# Read configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Configuration parameters
DEBUG: bool = config.getboolean("Debug", "debug")
STEP_COUNT: int = config.getint("Debug", "step_count")
ACCESS_TOKEN: str | None = os.getenv("TOKEN")
USER: str = config.get("Settings", "github_user_name")
TIMEZONE: str = config.get("Settings", "target_tz")
target_tz = tz(TIMEZONE)

print(USER)

# Initialize GitHub API client
g = Github(ACCESS_TOKEN)
user = g.get_user(USER)


def count_lines(content: str) -> int:
    """
    Count the number of lines in a given string content.

    Args:
    - content (str): The content of a file.

    Returns:
    - int: The number of lines in the content.
    """
    return len(content.splitlines())


def count_python_constructs(content: str) -> tuple[set[str], dict[str, int]]:
    """
    Count the occurrences of various Python constructs in a given content string.

    Args:
    - content (str): The content of a Python file.

    Returns:
    - tuple[set[str], dict[str, int]]: A tuple containing a set of imported libraries
      and a dictionary with counts of various Python constructs such as 'if statements',
      'while loops', 'for loops', etc.
    """
    counts: dict[str, int] = {
        "if statements": 0,
        "while loops": 0,
        "for loops": 0,
        "regular functions created": 0,
        "async functions created": 0,
        "classes created": 0,
    }

    check_imports: bool = True
    importless_streak: int = 0
    libraries: set[str] = set()
    import_patterns = [r"^import\s+(\w+)", r"^from\s+(\w+)\s+import"]

    # Patterns for functions and classes
    async_function_pattern: str = r"async\s+def\s+\w+\b"
    function_pattern: str = r"\bdef\s+\w+\b"

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

        # Count various Python constructs in each line
        counts["if statements"] += len(re.findall(r"\bif\b", line))
        counts["while loops"] += len(re.findall(r"\bwhile\b", line))
        counts["for loops"] += len(re.findall(r"\bfor\b", line))

        # Count async functions first
        async_functions = len(re.findall(async_function_pattern, line))
        counts["async functions created"] += async_functions

        # Count all functions, subtract async functions to get regular functions
        all_functions = len(re.findall(function_pattern, line))
        counts["regular functions created"] += all_functions - async_functions

        counts["classes created"] += len(re.findall(r"\bclass\b", line))

    return libraries, counts


def is_recent_commit(commit_date: datetime) -> bool:
    """
    Check if a commit is recent (within the last 90 days).

    Args:
    - commit_date (datetime): The date of the commit.

    Returns:
    - bool: True if the commit is recent, False otherwise.
    """
    return commit_date >= datetime.now(timezone.utc) - timedelta(days=90)


# Initialize the main data structure to hold repository statistics
repo_data: dict[str, list | dict] = {
    "repo_stats": [],
    "commit_counts": {},
    "construct_counts": [],
    "recent_commits": [],
}

# Initialize a dictionary to hold commit messages and a list to hold commit times
commit_messages: defaultdict[str, list] = defaultdict(list)
commit_times: list[list[int]] = []

# Iterate over the user's repositories
repo_iter = iter(user.get_repos())
for i, repo in enumerate(repo_iter):
    if not repo.fork and not repo.archived:
        if DEBUG and i >= STEP_COUNT:
            break

        # Skip profile repo if specified in the configuration
        if (
            not config.getboolean("Settings", "include_profile_repo")
            and repo.name == user.login
        ):
            continue

        # Skip ignored repositories
        if repo.name in config.get("Settings", "ignored_repos"):
            continue

        # Skip repositories not owned by the user
        if repo.owner.login != user.login:
            continue

        print(f"Processing {repo.name}...")

        # Initialize commit data for the repository
        commits = repo.get_commits()
        total_commits: int = 0
        recent_commits: list[dict[str, str | int]] = []

        for commit in commits:
            commit_date = commit.commit.author.date
            commit_times.append([commit_date.weekday(), commit_date.hour])
            commit_messages[repo.name].append(commit.commit.message)
            total_commits += 1

            # Collect details of recent commits
            if is_recent_commit(commit_date):
                commit_details: dict[str, str | int] = {
                    "repo_name": repo.name,
                    "repo_url": f"https://github.com/{user.login}/{repo.name}",
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit_date.isoformat(),
                }

                commit_data = repo.get_commit(commit.sha)
                commit_details["additions"] = commit_data.stats.additions
                commit_details["deletions"] = commit_data.stats.deletions
                commit_details["total_changes"] = commit_data.stats.total

                recent_commits.append(commit_details)

        # Initialize repository statistics
        repo_info: dict[str, list | dict | int | str | set] = {
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

        # Process the contents of the repository
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                # Determine the file extension
                split_path = file_content.path.rsplit(".", 1)
                if len(split_path) > 1:
                    file_extension = "." + split_path[-1]
                else:
                    file_extension = file_content.path

                # Update file extension counts
                repo_info["file_extensions"][file_extension] = (
                    repo_info["file_extensions"].get(file_extension, 0) + 1
                )

                # Process Python files
                if file_extension == ".py":
                    repo_info["total_python_files"] += 1
                    if file_content.encoding == "base64":
                        try:
                            file_content_data = file_content.decoded_content.decode(
                                "utf-8"
                            )
                            repo_info["python_files"].append(file_content.path)
                            repo_info["total_python_lines"] += count_lines(
                                file_content_data
                            )
                            libs, construct_counts = count_python_constructs(
                                file_content_data
                            )
                            repo_info["libraries"].update(libs)

                            # Update the construct counts
                            for key in repo_info["construct_counts"]:
                                repo_info["construct_counts"][key] += construct_counts[
                                    key
                                ]

                        except UnicodeDecodeError:
                            print(f"Skipping non-UTF-8 file: {file_content.path}")
                    else:
                        print(
                            f"Skipping file with unsupported encoding: {file_content.path}"
                        )

        # Convert libraries set to list and add repo info to repo_data
        repo_info["libraries"] = list(repo_info["libraries"])
        repo_data["repo_stats"].append(repo_info)
        repo_data["recent_commits"].extend(recent_commits)

# Create a DataFrame for commit times
commit_df = pd.DataFrame(commit_times, columns=["DayOfWeek", "HourOfDay"])

# Verify that 'HourOfDay' and 'DayOfWeek' are correctly created
print(commit_df.head())
print(commit_df.columns)

# Ensure 'HourOfDay' exists and has values
if "HourOfDay" not in commit_df.columns:
    raise KeyError("The 'HourOfDay' column is missing from the DataFrame!")

# Map weekdays to their names
weekday_map = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
commit_df["DayOfWeek"] = commit_df["DayOfWeek"].map(weekday_map)

# Group commit data by day and hour, and count the occurrences
commit_counts = (
    commit_df.groupby(["DayOfWeek", "HourOfDay"]).size().reset_index(name="Count")
)

# Verify that the grouped DataFrame is correctly structured
print(commit_counts.head())

# Build the commit counts dictionary
commit_counts_dict: dict[str, dict[int, int]] = {}
for _, row in commit_counts.iterrows():
    day: str = row["DayOfWeek"]
    hour: int = row["HourOfDay"]
    count: int = row["Count"]
    if day not in commit_counts_dict:
        commit_counts_dict[day] = {}
    commit_counts_dict[day][hour] = count

# Assign the commit counts dictionary to repo_data
repo_data["commit_counts"] = commit_counts_dict

# Print debug information if debugging is enabled
if DEBUG:
    print(f"Debug information: {repo_data}")

# Write repository data to a JSON file
with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)
