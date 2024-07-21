from github import Github
from dotenv import load_dotenv
import os
import json
import configparser
from collections import defaultdict

load_dotenv()

ACCESS_TOKEN = os.getenv("TOKEN")
config = configparser.ConfigParser()
config.read("config.ini")
USER = config.get("Settings", "github_user_name")

g = Github(ACCESS_TOKEN)

user = g.get_user(USER)

# Load existing repo_data JSON
with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Initialize a dictionary to store commit messages
commit_messages = defaultdict(list)

for repo in user.get_repos():
    # Only process repositories that are not forks
    if not repo.fork:
        print(f"Fetching commit messages for {repo.name}...")
        for commit in repo.get_commits():
            commit_messages[repo.name].append(commit.commit.message)

# Add commit messages to repo_data
for repo_info in repo_data["repo_stats"]:
    repo_name = repo_info["repo_name"]
    if repo_name in commit_messages:
        repo_info["commit_messages"] = commit_messages[repo_name]

# Save the updated data as JSON
with open("repo_data.json", "w") as json_file:
    json.dump(repo_data, json_file, indent=4)

print("Commit messages added to repo_data.json")
