import json
import plotly.express as px
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

GENERATE = config.getboolean("Settings", "generate_lines_of_code_pr_scatter_chart")

with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

sorted_repos = sorted(repo_data["repo_stats"], key=lambda x: x["total_python_lines"], reverse=True)

top_repos = sorted_repos[:7]
repo_names = [repo["repo_name"] for repo in top_repos]
lines_of_code = [repo["total_python_lines"] for repo in top_repos]
total_commits = [repo["total_commits"] for repo in top_repos]

df = pd.DataFrame(
    {"Repository Name": repo_names, "Lines of Python Code": lines_of_code, "Total Commits": total_commits}
)

fig = px.scatter(
    df,
    x="Repository Name",
    y="Lines of Python Code",
    size="Total Commits",
    color="Total Commits",
    text="Lines of Python Code",
    color_continuous_scale=px.colors.sequential.Viridis,
)

fig.update_traces(
    line=dict(width=7),
    marker=dict(size=df["Total Commits"] * 10),
    texttemplate="%{x} <br> Lines of Code: %{y}<br>Total Commits: %{text}",
    text=[f"{size // 10}" for size in df["Total Commits"] * 10],
    textposition="bottom center",
)

fig.update_layout(
    title="Repos by Lines of Python Code and Total Commits",
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    xaxis=dict(
        showgrid=False,
        showticklabels=True,
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=True,
        zeroline=False,
        visible=True,
        showline=False,
        range=[0, df["Lines of Python Code"].max() + 100],
    ),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=60, b=0),
)

if GENERATE:
    fig.write_image("DataVisuals/top_lines_prs.png", width=1200, height=800)
    print("Lines of code and total commits scatter plot generated successfully.")
else:
    print("Lines of code and total commits scatter plot not generated.")
