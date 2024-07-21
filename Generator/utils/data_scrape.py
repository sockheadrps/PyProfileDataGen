from github import Github
from dotenv import load_dotenv
import os
import json
import re
from collections import defaultdict
import pandas as pd

load_dotenv()

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

for repo in user.get_repos():
    if not repo.fork:
        print(f"Processing {repo.name}...")
        commits = repo.get_commits()
        for commit in commits:
            commit_date = commit.commit.author.date
            commit_times.append([commit_date.weekday(), commit_date.hour])
            commit_messages[repo.name].append(commit.commit.message)

        repo_info = {
            "repo_name": repo.name,
            "python_files": [],
            "libraries": set(),
            "total_python_lines": 0,
            "file_extensions": {},
            "total_commits": 0,
            "commit_messages": commit_messages[repo.name],  # Add commit messages
            "construct_counts": {},  # Add construct counts
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
                            repo_info["construct_counts"] = construct_counts  # Add construct counts to repo_info
                        except UnicodeDecodeError:
                            print(f"Skipping non-UTF-8 file: {file_content.path}")
                    else:
                        print(f"Skipping file with unsupported encoding: {file_content.path}")

        repo_info["libraries"] = list(repo_info["libraries"])
        repo_data["repo_stats"].append(repo_info)

# Convert commit_times to a DataFrame
commit_df = pd.DataFrame(commit_times, columns=["DayOfWeek", "HourOfDay"])

# Map weekdays to labels
weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
commit_df["DayOfWeek"] = commit_df["DayOfWeek"].map(weekday_map)

# Count the number of commits for each hour of the day and day of the week
commit_counts = commit_df.groupby(["DayOfWeek", "HourOfDay"]).size().reset_index(name="Count")

# Add commit counts to repo_data
repo_data["commit_counts"] = commit_counts.to_dict(orient="records")

# Save the data as JSON
with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)
