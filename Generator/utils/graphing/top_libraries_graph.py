import json
from collections import Counter
import plotly.graph_objects as go
import configparser


config = configparser.ConfigParser()
config.read("config.ini")

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

fig.update_layout(
    title="Top 15 Libraries Used Across Repositories",
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    margin=dict(l=40, r=40, t=60, b=100),
    hovermode="x unified",
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)


if GENERATE:
    fig.write_image("DataVisuals/top_libraries.png", width=1200, height=800)
    print("Top libraries graph generated successfully.")
else:
    print("Top libraries graph not generated.")
