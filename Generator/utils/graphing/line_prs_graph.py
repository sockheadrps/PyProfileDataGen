import json
import plotly.express as px
import pandas as pd
import configparser

# Load the configuration settings from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Read the setting to determine if the scatter chart should be generated
GENERATE: bool = config.getboolean(
    "Settings", "generate_lines_of_code_pr_scatter_chart"
)

# Load the repository data from a JSON file
with open("repo_data.json", "r") as json_file:
    repo_data: dict = json.load(json_file)

# Sort repositories by the total number of Python lines of code in descending order
sorted_repos: list[dict] = sorted(
    repo_data["repo_stats"], key=lambda x: x["total_python_lines"], reverse=True
)

# Select the top 7 repositories based on the number of Python lines of code
top_repos: list[dict] = sorted_repos[:7]
repo_names: list[str] = [repo["repo_name"] for repo in top_repos]
lines_of_code: list[int] = [repo["total_python_lines"] for repo in top_repos]
total_commits: list[int] = [repo["total_commits"] for repo in top_repos]

# Create a DataFrame for the top repositories with their names, lines of code, and total commits
df: pd.DataFrame = pd.DataFrame(
    {
        "Repository Name": repo_names,
        "Lines of Python Code": lines_of_code,
        "Total Commits": total_commits,
    }
)

# Create a scatter plot using Plotly Express
fig = px.scatter(
    df,
    x="Repository Name",
    y="Lines of Python Code",
    size="Total Commits",
    color="Total Commits",
    text="Lines of Python Code",
    color_continuous_scale=px.colors.sequential.Viridis,  # Color scale for commit counts
)

# Update the trace to modify the appearance of the scatter points and text
fig.update_traces(
    line=dict(width=7),  # Set the width of the line
    marker=dict(
        size=df["Total Commits"] * 10
    ),  # Scale marker size based on total commits
    texttemplate="%{x} <br> Lines of Code: %{y}<br>Total Commits: %{text}",
    text=[f"{size // 10}" for size in df["Total Commits"] * 10],
    textposition="bottom center",
)

# Update layout settings for the chart
fig.update_layout(
    title="Repos by Lines of Python Code and Total Commits",
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    xaxis=dict(
        showgrid=False,  # Disable grid on x-axis
        showticklabels=True,  # Show tick labels on x-axis
    ),
    yaxis=dict(
        showgrid=False,  # Disable grid on y-axis
        showticklabels=True,  # Show tick labels on y-axis
        zeroline=False,  # Do not show the zero line
        visible=True,
        showline=False,
        range=[0, df["Lines of Python Code"].max() + 100],  # Set y-axis range
    ),
    plot_bgcolor="#22272E",  # Dark Gray Background
    paper_bgcolor="#22272E",  # Dark Gray Paper Background
    margin=dict(l=40, r=40, t=60, b=0),
)

# Check if the scatter chart should be generated and saved as an image
if GENERATE:
    fig.write_image("DataVisuals/top_lines_prs.png", width=1200, height=800)
    print("Lines of code and total commits scatter plot generated successfully.")
else:
    print("Lines of code and total commits scatter plot not generated.")
