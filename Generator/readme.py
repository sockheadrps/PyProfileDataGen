import json
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
import os
import configparser

# Load configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Configuration flags
SHOW_RECENT_COMMITS: bool = config.getboolean("Readme", "show_recent_commits")
GENERATE_MERGED_PRS: bool = config.getboolean("Readme", "generate_merged_prs")
SHOW_TOTAL_LINES_OF_CODE: bool = config.getboolean("Readme", "show_total_lines_of_code")
SHOW_TOTAL_LIBS: bool = config.getboolean("Readme", "show_total_libs_used")


def load_environment() -> list[str]:
    """
    Load environment variables and configuration settings.

    Returns:
    - list[str]: A list of libraries to be excluded from the metrics.
    """
    load_dotenv()

    global TODAY, GITHUB_RUN_ID
    TODAY = os.getenv("TODAY")
    GITHUB_RUN_ID = os.getenv("GITHUB_RUN_ID")

    config = configparser.ConfigParser()
    config.read("config.ini")
    excluded_libraries_str = config.get(
        "ExcludedLibs", "excluded_libraries", fallback=""
    )
    excluded_libraries = eval(excluded_libraries_str)

    return excluded_libraries


def load_repo_data() -> dict:
    """
    Load the repository data from a JSON file.

    Returns:
    - dict: The data loaded from the 'repo_data.json' file, or an empty dictionary if the file is not found or is invalid.
    """
    with open("repo_data.json", "r") as json_file:
        return json.load(json_file)



def calculate_library_metrics(
    repo_data: dict, excluded_libraries: list[str, ...]
) -> tuple
        [
            int,
            int,
            int,
            list[tuple[str, int], ...],
            tuple[str, ...],
            tuple[int, ...]
        ]:
    """
    Calculate various library-related metrics from the repository data.

    Args:
    - repo_data (dict): The data of repositories containing stats and libraries used.
    - excluded_libraries (list[str]): A list of libraries to be excluded from the metrics.

    Returns:
    - tuple: A tuple containing the following metrics:
        - total_lines_of_code (int): The total lines of Python code.
        - total_libraries_used (int): The total number of unique libraries used.
        - total_python_files (int): The total number of Python files.
        - top_libraries (list[tuple[str, int]]): The top 15 most used libraries and their counts.
        - libraries (tuple[str]): The names of the top libraries.
        - counts (tuple[int]): The usage counts of the top libraries.
    """
    library_counts: Counter = Counter()
    libraries_used: set[str | None, ...] = set()
    total_python_files: int = 0

    for repo in repo_data["repo_stats"]:
        for library in repo["libraries"]:
            if library not in excluded_libraries:
                library_counts[library] += 1
                libraries_used.update(repo["libraries"])

        total_python_files += repo["total_python_files"]

    total_lines_of_code: int = sum(
        repo["total_python_lines"] for repo in repo_data["repo_stats"]
    )
    total_libraries_used: int = len(libraries_used)

    top_libraries: list[tuple[str, int], ...] = library_counts.most_common(15)
    libraries:tuple[str], counts:tuple[int] = zip(*top_libraries)

    return (
        total_lines_of_code,
        total_libraries_used,
        total_python_files,
        top_libraries,
        libraries,
        counts,
    )


def format_recent_commits(commits: list[dict, ...]) -> str:
    """
    Format the recent commits for display in the README.

    Args:
    - commits (list[dict]): A list of recent commits with details.

    Returns:
    - str: A formatted string containing the recent commits.
    """
    sorted_commits = sorted(
        commits, key=lambda x: datetime.fromisoformat(x["date"]), reverse=True
    )

    formatted_commits: list[tuple | None, ...] = []
    for commit in sorted_commits[:3]:
        clean_message: str = commit["message"].replace("\n", " ").replace("\r", " ").strip()
        commit_info: tuple[str] = (
            f'- **{commit["repo_name"]} - [{clean_message}]({commit["repo_url"]}/commit/{commit["sha"]})**\n'
            f'  - Additions: {commit["additions"]} - Deletions: {commit["deletions"]} - Total Changes: {commit["total_changes"]}\n'
        )
        formatted_commits.append(commit_info)

    return "\n".join(formatted_commits)


def format_pr_info(prs: list[dict, ...]) -> str:
    """
    Format the pull request information for display in the README.

    Args:
    - prs (list[dict]): A list of merged pull requests with details.

    Returns:
    - str: A formatted string containing the pull request information.
    """
    formatted_info: list[tuple | None, ...] = []
    for pr in prs:
        pr_info: tuple[str] = (
            f'- **[{pr["title"]}]({pr["url"]})**\n'
            f'  - Repository: [{pr["repository"]}]({pr["repo_url"]})\n'
            f'  - Stars: {pr["stars"]}\n'
        )
        formatted_info.append(pr_info)
    return "\n".join(formatted_info)


def update_readme() -> None:
    """
    Update the README file with the latest metrics and commit/PR information.
    """
    excluded_libraries = load_environment()
    repo_data = load_repo_data()
    (
        total_lines_of_code,
        total_libraries_used,
        total_python_files,
        top_libraries,
        libraries,
        counts,
    ): tuple[int, int, int, tuple[str, int], tuple[str], tuple[int]] = calculate_library_metrics(repo_data, excluded_libraries)

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
        total_libraries_used = (
            f"### Total Libraries/Modules Imported: {total_libraries_used}\n"
        )
    else:
        total_libraries_used = "\n\n"

    total_python_files_section = f"### Total Python Files: {total_python_files}\n"

    new_metrics_section: list[str, ...] = [
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

    # Read existing README content
    with open(readme_file, "r", encoding="utf-8") as file_object:
        lines: list[str, ...] = file_object.readlines()

    # Find the position of '---' in the existing content
    split_index: int = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            split_index = i
            break

     # Update README content
    updated_lines: str = lines[: split_index + 1]  # Include the '---' line
    updated_lines += new_metrics_section

    # Write the updated content back to README
    with open(readme_file, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


# Main execution
if __name__ == "__main__":
    update_readme()
