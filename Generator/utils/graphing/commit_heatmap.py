import json
import pandas as pd
import plotly.express as px
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")
GENERATE = config.getboolean("Settings", "generate_commit_heatmap")

# Read data from JSON file
with open("repo_data.json", "r") as file:
    data = json.load(file)

# Extract commit counts data
commit_counts = data["commit_counts"]

# Convert the nested dictionary to a DataFrame
commit_counts_df = pd.DataFrame(commit_counts).fillna(0).astype(int).T
commit_counts_df.index.name = "DayOfWeek"
commit_counts_df.columns.name = "HourOfDay"

# Convert hour column names to integer for sorting
commit_counts_df.columns = commit_counts_df.columns.astype(int)

# Function to convert hour to AM/PM format
def hour_to_am_pm(hour):
    return f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"

# Reindex the DataFrame to ensure the correct order
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
hours_order = list(range(24))

commit_counts_df = commit_counts_df.reindex(ordered_days).reindex(columns=hours_order)
commit_counts_df.columns = commit_counts_df.columns.map(hour_to_am_pm)

# Create heatmap
fig = px.imshow(
    commit_counts_df,
    labels=dict(x="Hour of Day", y="Day of Week", color="Commit Count"),
    x=commit_counts_df.columns,
    y=commit_counts_df.index,
    color_continuous_scale="plasma",  # Changed to plasma color scheme
    aspect="auto",
)

# Update layout for better aesthetics
fig.update_layout(
    title="Heatmap of Commit Frequency by Hour of Day and Day of Week",
    xaxis_nticks=24,
    yaxis_nticks=7,
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    xaxis=dict(tickfont=dict(color="white")),
    yaxis=dict(tickfont=dict(color="white")),
    coloraxis_colorbar=dict(tickfont=dict(color="white")),
)

# Save the heatmap image if configured to generate
if GENERATE:
    fig.write_image("DataVisuals/commit_heatmap.png", width=1200, height=800)
    print("Commit heatmap generated successfully.")
else:
    print("Commit heatmap not generated.")
