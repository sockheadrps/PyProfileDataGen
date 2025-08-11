import json
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config_helper import config

GENERATE = config.getboolean("Settings", "generate_construct_bar_chart")

# Load repo data from JSON
with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Aggregate construct counts across all repositories
aggregate_construct_count = defaultdict(int)

for repo in repo_data["repo_stats"]:
    construct_counts = repo.get("construct_counts", {})
    for construct, count in construct_counts.items():
        aggregate_construct_count[construct] += count

# Convert aggregate_construct_count to a DataFrame
df = pd.DataFrame(list(aggregate_construct_count.items()), columns=["Construct", "Count"])

# Get top 15 constructs
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

# Create figure for construct counts
fig = go.Figure(
    data=[
        go.Bar(
            x=df["Construct"],
            y=df["Count"],
            text=df["Count"],
            textposition="auto",
            marker_color=colors[: len(df)],
            textfont=dict(size=14, weight="bold"),
        )
    ]
)

fig.update_layout(
    title="Python Construct Counts",
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=60, b=100),
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)

if GENERATE:
    fig.write_image("DataVisuals/construct_counts.png", width=1200, height=800)
    print("Construct counts graph generated successfully.")
else:
    print("Construct counts graph not generated.")