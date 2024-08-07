import json
import plotly.graph_objects as go
import pandas as pd
import configparser
from collections import defaultdict

config = configparser.ConfigParser()
config.read("config.ini")

GENERATE = config.getboolean("Settings", "generate_file_types_bar_chart")
EXCLUDED_FILE_TYPES = config.get("ExcludedFileTypes", "excluded_file_types")

# Load repo data from JSON
with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Aggregate file extensions counts across all repositories
aggregate_file_extension_count = defaultdict(int)

for repo in repo_data["repo_stats"]:
    file_extensions = repo.get("file_extensions", {})
    if ".py" in file_extensions:
        for extension, count in file_extensions.items():
            if extension != ".py" and extension not in EXCLUDED_FILE_TYPES:
                aggregate_file_extension_count[extension] += count


# Convert aggregate_file_extension_count to a DataFrame
df = pd.DataFrame(list(aggregate_file_extension_count.items()), columns=["File Type", "Count"])

# Sort by count and get top 15 file types
df = df.sort_values(by="Count", ascending=False).head(15)

# Define colors for bar chart
colors = [
    "#ff6f61",
    "#a4e4b1",
    "#ffb347",
    "#4ecdc4",
    "#d1ccc0",
    "#ff6b6b",
    "#6ab04c",
    "#d6a2e8",
    "#ff9ff3",
    "#7bed9f",
    "#feca57",
    "#1abc9c",
    "#ff6348",
    "#686de0",
    "#ff4757",
]

# Create figure for file types counts
fig = go.Figure(
    data=[
        go.Bar(
            x=df["File Type"],
            y=df["Count"],
            text=df["Count"],
            textposition="auto",
            marker_color=colors[: len(df)],
            textfont=dict(size=14, weight="bold"),
        )
    ]
)

fig.update_layout(
    title="File Types Counts",
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=60, b=100),
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)

if GENERATE:
    fig.write_image("DataVisuals/file_types_counts.png", width=1200, height=800)
    print("File types counts graph generated successfully.")
else:
    print("File types counts graph not generated.")
