import json
from collections import Counter
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config_helper import config

GENERATE = config.getboolean("Settings", "generate_libs_used_bar_chart")
EXCLUDED_LIBS = config.get("ExcludedLibs", "excluded_libraries")

# Load repo data from JSON
with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Count libraries used
library_counts = Counter()

for repo in repo_data["repo_stats"]:
    for library in repo["libraries"]:
        if library not in EXCLUDED_LIBS:
            library_counts[library] += 1

# Get top 15 libraries
top_libraries = library_counts.most_common(15)
libraries, counts = zip(*top_libraries)

# Parse excluded libraries for display
excluded_libs_list = []
if EXCLUDED_LIBS:
    try:
        # Try to parse as JSON first
        import ast
        excluded_libs_list = ast.literal_eval(EXCLUDED_LIBS)
        if not isinstance(excluded_libs_list, list):
            excluded_libs_list = [EXCLUDED_LIBS]
    except:
        # Fallback to comma-separated
        excluded_libs_list = [lib.strip() for lib in EXCLUDED_LIBS.split(",") if lib.strip()]

# Define colors for the bar chart
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

# Create figure for top 15 libraries
fig = go.Figure(
    data=[
        go.Bar(
            x=libraries,
            y=counts,
            text=counts,
            textposition="auto",
            marker_color=colors,
            textfont=dict(size=18, weight="bold"),
        )
    ]
)

# Create title with excluded libraries info
title_text = "Top 15 Libraries Used Across Repositories"
if excluded_libs_list:
    title_text += f"<br><sub>Excluded: {', '.join(excluded_libs_list)}</sub>"

fig.update_layout(
    title=title_text,
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=80, b=100),  # Increased top margin for longer title
    hovermode="x unified",
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)


if GENERATE:
    fig.write_image("DataVisuals/top_libraries.png", width=1200, height=800)
    print("Top libraries graph generated successfully.")
else:
    print("Top libraries graph not generated.")
