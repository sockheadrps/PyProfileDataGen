import json
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
import os
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

SHOW_RECENT_COMMITS = config.getboolean("Readme", "show_recent_commits")
GENERATE_MERGED_PRS = config.getboolean("Readme", "generate_merged_prs")
SHOW_TOTAL_LINES_OF_CODE = config.getboolean(
    "Readme", "show_total_lines_of_code")
SHOW_TOTAL_LIBS = config.getboolean("Readme", "show_total_libs_used")


# Function to load environment variables and configuration
def load_environment():
    load_dotenv()

    global TODAY, GITHUB_RUN_ID
    TODAY = os.getenv("TODAY")
    GITHUB_RUN_ID = os.getenv("GITHUB_RUN_ID")

    config = configparser.ConfigParser()
    config.read("config.ini")
    excluded_libraries_str = config.get(
        "ExcludedLibs", "excluded_libraries", fallback="")
    excluded_libraries = eval(excluded_libraries_str)

    return excluded_libraries


def load_repo_data():
    with open("repo_data.json", "r") as json_file:
        return json.load(json_file)


def calculate_library_metrics(repo_data, excluded_libraries):
    library_counts = Counter()
    libraries_used = set()
    total_python_files = 0

    for repo in repo_data["repo_stats"]:
        for library in repo["libraries"]:
            if library not in excluded_libraries:
                library_counts[library] += 1
                libraries_used.update(repo["libraries"])

        total_python_files += repo["total_python_files"]

    total_lines_of_code = sum(repo["total_python_lines"]
                              for repo in repo_data["repo_stats"])
    total_libraries_used = len(libraries_used)

    top_libraries = library_counts.most_common(15)
    libraries, counts = zip(*top_libraries)

    return total_lines_of_code, total_libraries_used, total_python_files, top_libraries, libraries, counts


def format_recent_commits(commits):
    sorted_commits = sorted(
        commits, key=lambda x: datetime.fromisoformat(x["date"]), reverse=True)

    formatted_commits = []
    for commit in sorted_commits[:3]:
        clean_message = commit["message"].replace(
            "\n", " ").replace("\r", " ").strip()
        commit_info = (
            f'- **{commit["repo_name"]} - [{clean_message}]({commit["repo_url"]}/commit/{commit["sha"]})**\n'
            f'  - Additions: {commit["additions"]} - Deletions: {commit["deletions"]} - Total Changes: {commit["total_changes"]}\n'
        )
        formatted_commits.append(commit_info)

    return "\n".join(formatted_commits)


def format_pr_info(prs):
    formatted_info = []
    for pr in prs:
        pr_info = (
            f'- **[{pr["title"]}]({pr["url"]})**\n'
            f'  - Repository: [{pr["repository"]}]({pr["repo_url"]})\n'
            f'  - Stars: {pr["stars"]}\n'
        )
        formatted_info.append(pr_info)
    return "\n".join(formatted_info)


def update_readme():
    excluded_libraries = load_environment()
    repo_data = load_repo_data()
    total_lines_of_code, total_libraries_used, total_python_files, top_libraries, libraries, counts = calculate_library_metrics(
        repo_data, excluded_libraries
    )

    readme_file = "README.md"
    timestamp = datetime.now().strftime("%Y-%m-%d")

    if SHOW_RECENT_COMMITS:
        recent_commits_section = f"## 🚀 Recent Commits\n\n{format_recent_commits(repo_data['recent_commits'])}\n\n"
    else:
        recent_commits_section = ""

    if GENERATE_MERGED_PRS:
        recent_prs_section = f"## 🔀 Recently Merged Pull Requests\n\n{format_pr_info(repo_data['merged_prs'][:3])}\n"
    else:
        recent_prs_section = ""

    if SHOW_TOTAL_LINES_OF_CODE:
        total_lines_of_code = f"### Total Lines of Python Code: {total_lines_of_code}\n"
    else:
        total_lines_of_code = ""

    if SHOW_TOTAL_LIBS:
        total_libraries_used = f"### Total Libraries/Modules Imported: {total_libraries_used}\n"
    else:
        total_libraries_used = "\n\n"

    total_python_files_section = f"### Total Python Files: {total_python_files}\n"

    new_metrics_section = [
        f"\n\n",
        f"### Data last generated on: {timestamp} via [GitHub Action {GITHUB_RUN_ID}](https://github.com/sockheadrps/sockheadrps/actions/runs/{GITHUB_RUN_ID})\n\n"
        f"{recent_commits_section}",
        f"{recent_prs_section}",
        f"# 📊 Python Stats:\n\n",
        f"{total_lines_of_code}",
        f"{total_libraries_used}",
        f"{total_python_files_section}",
        f"![](DataVisuals/data.gif)\n\n",
    ]

    with open(readme_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the position of '---' in the existing content
    split_index = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            split_index = i
            break

    updated_lines = lines[: split_index + 1]  # Include the '---' line
    updated_lines += new_metrics_section

    with open(readme_file, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


# Main execution
if __name__ == "__main__":
    update_readme()
