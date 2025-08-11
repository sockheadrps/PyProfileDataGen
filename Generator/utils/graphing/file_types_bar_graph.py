import json
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config_helper import config

GENERATE = config.getboolean("Settings", "generate_file_types_bar_chart")
EXCLUDED_FILE_TYPES = config.get("ExcludedFileTypes", "excluded_file_types")

# Load repo data from JSON
with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Parse excluded file types for comparison
excluded_file_types_list = []
if EXCLUDED_FILE_TYPES:
    try:
        import ast
        excluded_file_types_list = ast.literal_eval(EXCLUDED_FILE_TYPES)
        if not isinstance(excluded_file_types_list, list):
            excluded_file_types_list = [EXCLUDED_FILE_TYPES]
    except:
        # Fallback to comma-separated
        excluded_file_types_list = [ft.strip() for ft in EXCLUDED_FILE_TYPES.split(",") if ft.strip()]

# Aggregate file extensions counts across all repositories
aggregate_file_extension_count = defaultdict(int)

for repo in repo_data["repo_stats"]:
    file_extensions = repo.get("file_extensions", {})
    if file_extensions:  # Check if file_extensions exists and is not empty
        for extension, count in file_extensions.items():
            if extension != ".py" and extension not in excluded_file_types_list:
                aggregate_file_extension_count[extension] += count


# Check if we have any file types to display
if not aggregate_file_extension_count:
    print("⚠️ No file types found to display. Check if file_extensions are populated in repo_data.json")
    # Create a placeholder DataFrame
    df = pd.DataFrame({"File Type": ["No data"], "Count": [0]})
else:
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

# Create title with excluded file types info
title_text = "File Types Counts"
if excluded_file_types_list:
    title_text += f"<br><sub>Excluded: {', '.join(excluded_file_types_list)}</sub>"

fig.update_layout(
    title=title_text,
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=80, b=100),  # Increased top margin for longer title
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)

if GENERATE:
    fig.write_image("DataVisuals/file_types_counts.png", width=1200, height=800)
    print("File types counts graph generated successfully.")
else:
    print("File types counts graph not generated.")
