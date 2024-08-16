import requests
import json
import configparser

# Load configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Get the GitHub username from the configuration
USERNAME = config.get("Settings", "github_user_name")


def fetch_merged_prs() -> list[dict[str, str | int]]:
    """
    Fetch merged pull requests authored by the user from the GitHub API.

    Returns:
    - list[dict[str, str | int]]: A list of dictionaries containing information
      about each merged pull request, including the PR number, title, repository
      name, repository URL, PR URL, creation and closing dates, and the author's
      username.
    """
    url = "https://api.github.com/search/issues"

    # Parameters for the search query to find merged pull requests
    params = {
        "q": f"is:merged state:closed author:{USERNAME} type:pr",
    }

    response = requests.get(url, params=params)
    merged_prs: list[dict[str, str | int]] = []

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        for item in items:
            # Extract the repository URL without the pull request part
            repo_url = item["html_url"].split("/pull")[0]

            # Skip PRs from the user's own repositories
            if USERNAME not in repo_url:
                # Extract repository name from the URL
                repo_name = repo_url.split("/")[-1]

                pr_info = {
                    "number": item["number"],
                    "title": item["title"],
                    "repository": repo_name,
                    "repo_url": repo_url,
                    "url": item["html_url"],
                    "created_at": item["created_at"],
                    "closed_at": item["closed_at"],
                    "author": item["user"]["login"],
                }

                merged_prs.append(pr_info)
    else:
        print(f"Request failed with status code {response.status_code}")

    return merged_prs


def fetch_star_count(repo_url: str) -> int:
    """
    Fetch the star count of a given GitHub repository.

    Args:
    - repo_url (str): The URL of the repository.

    Returns:
    - int: The number of stars the repository has. Returns 0 if the request fails.
    """
    # Construct the API URL for the repository
    repo_api_url = f'https://api.github.com/repos/{"/".join(repo_url.split("/")[-2:])}'

    response = requests.get(repo_api_url)

    if response.status_code == 200:
        repo_data = response.json()
        return repo_data.get("stargazers_count", 0)
    else:
        print(
            f"Failed to fetch star count for {repo_url} with status code {response.status_code}"
        )
        return 0


def update_repo_data_with_merged_prs() -> None:
    """
    Update the repo_data.json file with merged pull requests and their corresponding
    star counts.

    This function fetches merged pull requests authored by the user, updates each
    with the star count of the repository, and then saves the updated information
    back to the repo_data.json file.
    """
    # Load existing repository data from JSON file
    with open("repo_data.json", "r") as f:
        repo_data = json.load(f)

    # Fetch merged PRs and their associated repositories
    merged_prs = fetch_merged_prs()

    # Fetch star count for each repository and update the PR data
    for pr in merged_prs:
        repo_url = pr.get("repo_url")
        if repo_url:
            pr["stars"] = fetch_star_count(repo_url)
        else:
            pr["stars"] = 0

    # Append the merged PRs with star counts to the repo_data dictionary
    repo_data["merged_prs"] = merged_prs

    # Save the updated repo_data back to the JSON file
    with open("repo_data.json", "w") as f:
        json.dump(repo_data, f, indent=4)


# Update repo_data.json with merged PRs and star counts
update_repo_data_with_merged_prs()
