import requests
import json
import configparser

from config_helper import config

USERNAME = config.get("Settings", "github_user_name")


def fetch_merged_prs():
    url = "https://api.github.com/search/issues"

    # Parameters for the search query - get recent merged PRs
    params = {
        "q": f"is:merged state:closed author:{USERNAME} type:pr",
        "sort": "updated",  # Sort by most recently updated
        "order": "desc",    # Descending order
        "per_page": 100     # Get more PRs to work with
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
                owner_name = repo_url.split("/")[-2]  # Extract owner name from URL

                pr_info = {
                    "number": item["number"],
                    "title": item["title"],
                    "repository": repo_name,
                    "owner": owner_name,
                    "repo_url": repo_url,
                    "url": item["html_url"],
                    "created_at": item["created_at"],
                    "closed_at": item["closed_at"],
                    "author": item["user"]["login"],
                    "stars": 0,  # Will be populated later
                    "full_repo_name": f"{owner_name}/{repo_name}"
                }

                merged_prs.append(pr_info)
    else:
        print(f"Request failed with status code {response.status_code}")

    return merged_prs


def fetch_star_count(repo_url):
    repo_api_url = f'https://api.github.com/repos/{"/".join(repo_url.split("/")[-2:])}'
    
    # Add headers to avoid rate limiting issues
    headers = {
        'User-Agent': 'GitHub-Stats-Collector',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(repo_api_url, headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            return repo_data.get("stargazers_count", 0)
        elif response.status_code == 403:
            print(f"⚠️ Rate limited while fetching stars for {repo_url}")
            return 0
        else:
            print(f"⚠️ Failed to fetch star count for {repo_url} with status code {response.status_code}")
            return 0
    except Exception as e:
        print(f"⚠️ Error fetching stars for {repo_url}: {e}")
        return 0


def update_repo_data_with_merged_prs():
    print("🔍 Fetching recently merged pull requests...")
    
    with open("repo_data.json", "r") as f:
        repo_data = json.load(f)

    merged_prs = fetch_merged_prs()
    print(f"📊 Found {len(merged_prs)} merged PRs")

    # Fetch star count for each repository
    print("⭐ Fetching star counts for repositories...")
    for i, pr in enumerate(merged_prs, 1):
        repo_url = pr.get("repo_url")
        if repo_url:
            stars = fetch_star_count(repo_url)
            pr["stars"] = stars
            print(f"  {i}/{len(merged_prs)}: {pr['full_repo_name']} - {stars} stars")
        else:
            pr["stars"] = 0

    # Sort by stars (highest first) and then by recency
    merged_prs.sort(key=lambda x: (x["stars"], x["closed_at"]), reverse=True)
    
    print(f"🏆 Top 5 PRs by stars:")
    for i, pr in enumerate(merged_prs[:5], 1):
        print(f"  {i}. {pr['full_repo_name']} - {pr['stars']} stars - {pr['title'][:50]}...")

    # Append merged PRs to repo_data dictionary
    repo_data["merged_prs"] = merged_prs

    with open("repo_data.json", "w") as f:
        json.dump(repo_data, f, indent=4)
    
    print(f"💾 Saved {len(merged_prs)} merged PRs to repo_data.json")


# update repo_data.json with merged PRs and star counts
update_repo_data_with_merged_prs()
