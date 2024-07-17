import json
import plotly.express as px
import pandas as pd
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

GENERATE = config.getboolean("Settings", "generate_lines_of_code_line_chart")

with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Sort repositories by lines of code
sorted_repos = sorted(repo_data["repo_stats"], key=lambda x: x["total_python_lines"], reverse=True)

# Get top 7 repositories
top_repos = sorted_repos[:7]
repo_names = [repo["repo_name"] for repo in top_repos]
lines_of_code = [repo["total_python_lines"] for repo in top_repos]
total_commits = [repo["total_commits"] for repo in top_repos]

# Create DataFrame
df = pd.DataFrame(
    {"Repository Name": repo_names, "Lines of Python Code": lines_of_code, "Total Commits": total_commits}
)

# Create line chart
fig = px.line(
    df,
    x="Repository Name",
    y="Lines of Python Code",
    line_shape="linear",  # Use linear line shape
    text="Lines of Python Code",
    labels={"Lines of Python Code": "Lines of Code"},  # Update y-axis label
    template="plotly_dark",  # Use dark theme template
)

fig.update_traces(
    texttemplate="%{y}",
    textposition="top center",
)

fig.update_layout(
    title="Repos by Lines of Python Code",
    xaxis_title="Repository Name",
    yaxis_title="Lines of Code",
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    xaxis=dict(
        showgrid=False,
        showticklabels=True,  # Show tick labels on x-axis
        tickangle=-45,  # Rotate x-axis labels for better readability
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=True,  # Show tick labels on y-axis
        zeroline=False,
        visible=True,
        showline=True,
        range=[0, df["Lines of Python Code"].max() + 100],
    ),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=60, b=0),
)


if GENERATE:
    fig.write_image("DataVisuals/top_lines.png", width=1200, height=800)
    print("Lines of code line chart generated successfully.")
else:
    print("Lines of code line chart not generated.")
