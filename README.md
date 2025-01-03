# Enhance Your GitHub Profile with Automated Data Insights and Visualizations

## Automatically showcase detailed analytics of your Python repositories via github actions.

### This tool automatically generates insightful data visualizations and key statistics for your repositories, updating your GitHub profile on every push. It seamlessly integrates with your existing profile and appends new information at the bottom so your content stays intact. The graphs that are generated are stitched together in a gif so your profile can remain concise and clean.

Analyze, generate and display visuals for your code in relation to:
- Repositories by commits, line count (of python code)
- A heatmap of your commit activity by day and time
- A word cloud of commit messages
- File type count
- Libraries used (Python)
- Construct counts (count of Loops, classes, control flow statements, async functions etc...)
- Highlights of your most recent closed PRs and commits

Keep your profile engaging with real-time data, without any extra work—everything runs automatically through GitHub Actions.


![](assets/profilegif.gif)

## Instructions

<details>
<summary>Making a Github API token</summary>

### Click your profile picture and go to Settings

![](assets/token-1.png)

### Click on Dev Settings

![](assets/token-2.png)

### Click on Token (classic) then Generate a new token (classic)

![](assets/token-3.png)

### Generate your Token

![](assets/token-4.png)

### Create a .env file in the root directory of your profile, make sure .env is in your .gitignore

```
TOKEN=YOUR_API_TOKEN
```

</details>

<details>
<summary>Saving Github API token for the github action</summary>

### Go to your profile repo and click on settings

![](assets/secret-1.png)

### Click on Secrets and Variables, then Actions, then New Repository Secret

![](assets/secret-2.png)

### Create a new secret with the name TOKEN, and use the github api key we generated, then click Add Secret

![](assets/secret-3.png)

</details>

<details>

<summary>Copy and save the config to your profile repo</summary>

### Copy the config from the [PyProfileDataGen repo](https://github.com/sockheadrps/PyProfileDataGen/blob/main/config.ini) to your profile repo.

![](assets/copyconfig.png)

### Paste this config into your profile repo as config.ini Edit the username value with your own, and any other configs you might want to change

![](assets/pasteconfig.png)

### open your profile README.md and add

```
---
```

to the end of the file.

Make sure --- doesnt appear anywhere else in your markdown. This is how the python script identifies the end of your readme.md to append / update data

![](assets/readmeadd.png)

</details>

<details>

<summary>Copy github workflow action into your profile repo</summary>
<br>

go to your github profile, add the directory .github/workflows and add a file, actions.yml. Paste the contents of [this action file](https://github.com/sockheadrps/PyProfileDataGen/blob/main/.github/workflows/actions.yml) into it.

![](assets/actionsfile.png)
![](assets/actionspaste.png)

</details>

<details>
<summary>Push to your profile repo</summary>
<br>

```
git add .
git commit -m "Updating profile"
git push
```

![](assets/push.png)

### Open your github profile repo and navigate to the build of your action you just initialized when you pushed

![](assets/workflow.png)

This will always take a few minutes if you have a lot of repos.

![](assets/actionfinished.png)

### Once this build finished your Profile will be updated and ready!

</details>

<details>
<summary>Starter Template</summary>
<br>

```
<!-- Badges https://github.com/inttter/md-badges -->
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54) 

<br>

<!-- Projects -->

### ***[NAME](LINK)***
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/USERNAME/REPO)  
***BRIEF DESCRIPTION***

<br>
<br>

<!-- Github Stats -->

![](https://github-readme-stats.vercel.app/api?username=USERNAME&theme=radical&hide_border=false&include_all_commits=true&count_private=false)<br/>
![](https://github-readme-stats.vercel.app/api/top-langs/?username=USERNAME&theme=radical&hide_border=false&include_all_commits=true&count_private=true&layout=compact)

## 🏆 GitHub Trophies

![](https://github-profile-trophy.vercel.app/?username=USERNAME&theme=radical&no-frame=false&no-bg=true&margin-w=4)

---

```

</details>

<details>

<summary>(Optional) Enable remote triggering of your github workflow action</summary>
<br>

If you want to trigger automated updates instead of manual updates to your Profile.  Go to your github repo where you would like to add auto triggering, add the directory .github/workflows and add a file, trigger.yml. Paste the contents of [this trigger file](https://github.com/sockheadrps/PyProfileDataGen/blob/main/.github/trigger.yml) into it and make a few simple changes listed below.

- Ensure that the ```secrets.TOKEN``` you previously created is added to the repo
    - Refer to [Saving Github API token for the github action](#go-to-your-profile-repo-and-click-on-settings)
- Change ```{owner}``` and ```{repo}``` to that of your profile ```actions.yml``` file
    - Example: ```https://api.github.com/repos/sockheadrps/sockheadrps/actions/workflows/actions.yml/dispatches```
- Change ```{current_repo}``` or the complete message
    - Example: ```"Triggered by One Awesome Repo"```

![](assets/triggerfile.png)

</details>