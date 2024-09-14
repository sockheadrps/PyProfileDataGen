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

<!-- Add any other content related to this section here -->

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

<summary>Clone this repo or save it from github and prepare your profile repo</summary>

### Clone or save

![](assets/clonesave.png)

### Open the folder you just saved this repo to, as well as the folder containing your profile repo. Move the highlighted files

![](assets/movefiles.png)

### open your profile README.md and add

```
---
```

to the end of the file.

Make sure --- doesnt appear anywhere else in your markdown. This is how the python script identifies the end of your readme.md to append / update data

![](assets/readmeadd.png)

### Open config.ini and edit the username value with your own, and any other configs you might want to change

![](assets/config.png)

</details>

<details>

<summary>(Optional) Test the data gen locally</summary>

go to your github profile page repo in your terminal and run:

```
python Generator\utils\data_scrape.py
```

This may take a few minutes depending on how many repos youve uploaded
![](assets/datascrape.png)

### Run the bat file

```
local_run.bat
```

### Or manually Run the following commands.

mergedprs.py must be run first

```
python Generator\utils\mergedprs.py
```

these can be run in any order

```
python Generator\utils\graphing\construct_counts_graph.py
```

```
python Generator\utils\graphing\line_prs_graph.py
```

```
python Generator\utils\graphing\lines_graph.py
```

```
python Generator\utils\graphing\top_libraries_graph.py
```

```
python Generator/utils/graphing/word_cloud.py
```

```
Generator/utils/graphing/commit_heatmap.py
```

```
python Generator\utils\graphing\file_types_bar_graph.py
```

then run

```
python Generator\utils\gifmaker.py
```

and finally run

```
python Generator\readme.py
```

![](assets/runlocal.png)

### Now look at the data appended in your README.md

</details>

<details>
<summary>Push to your profile repo</summary>
<br>
This pull isnt necessary on the initial commit of this, but after this first commit github Actions will be updating your readme automatically, meaning the readme.md will have changes that our local repo doesnt have. To resolve this any time we want to re-run our data generation, we should pull.

```
git pull
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
