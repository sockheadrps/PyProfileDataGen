import requests
import json
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

USERNAME = config.get("Settings", "github_user_name")


def fetch_merged_prs():
    url = "https://api.github.com/search/issues"

    # Parameters for the search query
    params = {
        "q": f"is:merged state:closed author:{USERNAME} type:pr",
    }

    response = requests.get(url, params=params)

    merged_prs = []

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        for item in items:
            repo_url = item["html_url"].split("/pull")[0]  # URL of the repository without the pull request part
            if USERNAME not in repo_url:
                repo_name = repo_url.split("/")[-1]  # Extract repo name from URL

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


def fetch_star_count(repo_url):
    repo_api_url = f'https://api.github.com/repos/{"/".join(repo_url.split("/")[-2:])}'
    response = requests.get(repo_api_url)
    if response.status_code == 200:
        repo_data = response.json()
        return repo_data.get("stargazers_count", 0)
    else:
        print(f"Failed to fetch star count for {repo_url} with status code {response.status_code}")
        return 0


def update_repo_data_with_merged_prs():
    with open("repo_data.json", "r") as f:
        repo_data = json.load(f)

    merged_prs = fetch_merged_prs()

    # Fetch star count for each repository
    for pr in merged_prs:
        repo_url = pr.get("repo_url")
        if repo_url:
            pr["stars"] = fetch_star_count(repo_url)
        else:
            pr["stars"] = 0

    # Append merged PRs to repo_data dictionary
    repo_data["merged_prs"] = merged_prs

    with open("repo_data.json", "w") as f:
        json.dump(repo_data, f, indent=4)


# update repo_data.json with merged PRs and star counts
update_repo_data_with_merged_prs()
