import json
from collections import Counter
import plotly.graph_objects as go
import configparser

# Read configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

# Read settings from the configuration file
GENERATE: bool = config.getboolean("Settings", "generate_libs_used_bar_chart")
EXCLUDED_LIBS: str = config.get("ExcludedLibs", "excluded_libraries")

# Load repository data from JSON file
with open("repo_data.json", "r") as json_file:
    repo_data: dict = json.load(json_file)

# Count occurrences of libraries used across repositories
library_counts: Counter = Counter()

# Iterate through each repository and count the libraries used
for repo in repo_data["repo_stats"]:
    for library in repo["libraries"]:
        if library not in EXCLUDED_LIBS:
            library_counts[library] += 1

# Get the top 15 most common libraries and their counts
top_libraries: list[tuple[str, int]] = library_counts.most_common(15)
libraries, counts = zip(*top_libraries)

# Define colors for the bar chart with color names
colors: list[str, ...] = [
    "#ff6f61",  # Coral Red
    "#a4e4b1",  # Light Mint Green
    "#ffb347",  # Pastel Orange
    "#4ecdc4",  # Turquoise
    "#d1ccc0",  # Warm Gray
    "#ff6b6b",  # Salmon Red
    "#6ab04c",  # Pistachio Green
    "#d6a2e8",  # Lavender
    "#ff9ff3",  # Light Pink
    "#7bed9f",  # Mint Green
    "#feca57",  # Saffron
    "#1abc9c",  # Jade Green
    "#ff6348",  # Tomato Red
    "#686de0",  # Periwinkle Blue
    "#ff4757",  # Ruby Red
]

# Create a bar chart figure for the top 15 libraries
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

# Update the layout of the figure
fig.update_layout(
    title="Top 15 Libraries Used Across Repositories",
    yaxis_title="Count",
    xaxis_tickangle=-45,
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    plot_bgcolor="#22272E",  # Dark Gray Background
    paper_bgcolor="#22272E",  # Dark Gray Paper Background
    margin=dict(l=40, r=40, t=60, b=100),
    hovermode="x unified",
    yaxis=dict(showticklabels=False, ticks="", showgrid=False, zeroline=False),
)

# Check if the graph should be generated based on the configuration setting
if GENERATE:
    # Save the graph as an image file
    fig.write_image("DataVisuals/top_libraries.png", width=1200, height=800)
    print("Top libraries graph generated successfully.")
else:
    print("Top libraries graph not generated.")
