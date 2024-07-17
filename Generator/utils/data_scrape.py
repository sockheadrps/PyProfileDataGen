from github import Github
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

ACCESS_TOKEN = os.getenv("TOKEN")


g = Github(ACCESS_TOKEN)

user = g.get_user()


def count_lines(content):
    return len(content.splitlines())


counts = {
    "if statements": 0,
    "while loops": 0,
    "for loops": 0,
    "functions created": 0,
    "async functions created": 0,
    "classes created": 0,
}


# Function to find Python libraries in a file content
def count_python_constructs(content):
    global counts
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
            # Break if there are more than 10 lines without imports in a row
            if importless_streak > 10:
                check_imports = False

        counts["if statements"] += len(re.findall(r"\bif\b", line))
        counts["while loops"] += len(re.findall(r"\bwhile\b", line))
        counts["for loops"] += len(re.findall(r"\bfor\b", line))
        counts["functions created"] += len(re.findall(r"\bdef\b", line))
        counts["async functions created"] += len(re.findall(r"\basync\s+def\b", line))
        counts["classes created"] += len(re.findall(r"\bclass\b", line))

    return libraries, counts


# Initialize repo_data JSON structure
repo_data = {"repo_stats": []}

for repo in user.get_repos():
    # Only process repositories that are not forks
    if not repo.fork:
        print(f"Processing {repo.name}...")
        repo_info = {
            "repo_name": repo.name,
            "python_files": [],
            "libraries": set(),
            "total_python_lines": 0,
            "file_extensions": {},
            "total_commits": 0,
        }

        contents = repo.get_contents("")

        while contents:
            commits = repo.get_commits()
            repo_info["total_commits"] = commits.totalCount
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file_extension = os.path.splitext(file_content.path)[1]

                # Update file extension count
                if file_extension in repo_info["file_extensions"]:
                    repo_info["file_extensions"][file_extension] += 1
                else:
                    repo_info["file_extensions"][file_extension] = 1

                # Only process .py files
                if file_extension == ".py":
                    # Check the encoding and decode if it's base64
                    if file_content.encoding == "base64":
                        try:
                            file_content_data = file_content.decoded_content.decode("utf-8")
                            repo_info["python_files"].append(file_content.path)
                            repo_info["total_python_lines"] += count_lines(file_content_data)
                            libs, construct_counts = count_python_constructs(file_content_data)
                            repo_info["libraries"].update(libs)

                        # Skip files that are not UTF-8 encoded, images, etc
                        except UnicodeDecodeError:
                            print(f"Skipping non-UTF-8 file: {file_content.path}")
                    else:
                        print(f"Skipping file with unsupported encoding: {file_content.path}")

        # Convert libraries set to list for JSON serialization
        repo_info["libraries"] = list(repo_info["libraries"])

        # Append repo_info to repo_stats
        repo_data["repo_stats"].append(repo_info)

        repo_data["construct_count"] = counts

# Save the data as JSON
with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)
