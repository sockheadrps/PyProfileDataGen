import json
import plotly.graph_objects as go
import pandas as pd
import configparser
from collections import defaultdict

# Load configuration settings from 'config.ini'
config = configparser.ConfigParser()
config.read("config.ini")

# Determine if the file types bar chart should be generated
GENERATE: bool = config.getboolean("Settings", "generate_file_types_bar_chart")

# Read excluded file types from the configuration
EXCLUDED_FILE_TYPES: list[str] = config.get("ExcludedFileTypes", "excluded_file_types")

# Load repository data from JSON file
with open("repo_data.json", "r") as json_file:
    repo_data: dict = json.load(json_file)

# Aggregate file extensions counts across all repositories
aggregate_file_extension_count: defaultdict[str, int] = defaultdict(int)

for repo in repo_data["repo_stats"]:
    file_extensions = repo.get("file_extensions", {})
    if ".py" in file_extensions:
        for extension, count in file_extensions.items():
            if extension != ".py" and extension not in EXCLUDED_FILE_TYPES:
                aggregate_file_extension_count[extension] += count

# Convert aggregate file extension counts to a DataFrame
df: pd.DataFrame = pd.DataFrame(
    list(aggregate_file_extension_count.items()), columns=["File Type", "Count"]
)

# Sort by count and select the top 15 file types
df = df.sort_values(by="Count", ascending=False).head(15)

# Define colors for the bar chart
# Color names are provided alongside hexadecimal codes
colors: list[str] = [
    "#ff6f61",  # Coral
    "#a4e4b1",  # Light Green
    "#ffb347",  # Light Orange
    "#4ecdc4",  # Turquoise
    "#d1ccc0",  # Light Beige
    "#ff6b6b",  # Light Red
    "#6ab04c",  # Green
    "#d6a2e8",  # Light Purple
    "#ff9ff3",  # Light Pink
    "#7bed9f",  # Light Mint
    "#feca57",  # Light Yellow
    "#1abc9c",  # Teal
    "#ff6348",  # Tomato Red
    "#686de0",  # Medium Blue
    "#ff4757",  # Red
]

# Create a bar chart figure to visualize file type counts
fig = go.Figure(
    data=[
        go.Bar(
            x=df["File Type"],
            y=df["Count"],
            text=df["Count"],
            textposition="auto",
            marker_color=colors[: len(df)],  # Assign colors to bars
            textfont=dict(size=14, weight="bold"),
        )
    ]
)

# Update layout settings for the bar chart
fig.update_layout(
    title="File Types Counts",
    yaxis_title="Count",
    xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
    font=dict(
        family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"
    ),  # Font settings
    plot_bgcolor="#22272E",  # Dark Gray Background
    paper_bgcolor="#22272E",  # Dark Gray Paper Background
    margin=dict(l=40, r=40, t=60, b=100),
    yaxis=dict(
        showticklabels=False,  # Hide y-axis tick labels
        ticks="",  # Hide ticks on y-axis
        showgrid=False,  # Hide gridlines on y-axis
        zeroline=False,  # Hide zero line on y-axis
    ),
)

# Check if the chart should be saved as an image and generate the file
if GENERATE:
    fig.write_image("DataVisuals/file_types_counts.png", width=1200, height=800)
    print("File types counts graph generated successfully.")
else:
    print("File types counts graph not generated.")
