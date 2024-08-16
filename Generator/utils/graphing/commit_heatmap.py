import json
import pandas as pd
import plotly.express as px
import os


# Load commit count data from JSON file
with open("repo_data.json", "r") as file:
    data: dict = json.load(file)

# Flatten the commit_counts structure from the JSON to a list of dictionaries
commit_data: list[dict[str, int]] = []
for day, hours in data["commit_counts"].items():
    for hour, count in hours.items():
        commit_data.append({"DayOfWeek": day, "HourOfDay": int(hour), "Count": count})

# Convert the flattened data into a DataFrame
commit_counts: pd.DataFrame = pd.DataFrame(commit_data)


def hour_to_am_pm(hour: int) -> str:
    """
    Convert an hour in 24-hour format to 12-hour AM/PM format.

    Args:
        hour (int): The hour in 24-hour format.

    Returns:
        str: The hour converted to 12-hour AM/PM format.
    """
    return f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"


# Apply the hour_to_am_pm function to convert the HourOfDay column
commit_counts["HourOfDay"] = commit_counts["HourOfDay"].apply(hour_to_am_pm)

# Pivot the DataFrame to get the heatmap structure
heatmap_data: pd.DataFrame = commit_counts.pivot(
    index="DayOfWeek", columns="HourOfDay", values="Count"
).fillna(0)

# Ensure days are ordered properly
ordered_days: list[str, ...] = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
heatmap_data = heatmap_data.reindex(ordered_days)

# Ensure hours are ordered properly
hours_order: list[str, ...] = [
    f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}" for hour in range(24)
]
heatmap_data = heatmap_data.reindex(columns=hours_order)

# Create the heatmap using Plotly Express
fig = px.imshow(
    heatmap_data,
    labels=dict(x="Hour of Day", y="Day of Week", color="Commit Count"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    aspect="auto",
    color_continuous_scale="Plasma",  # Color scale for heatmap
    zmin=0,
    zmax=heatmap_data.max().max(),  # Set color scale max value
)

# Update layout of the heatmap
fig.update_layout(
    title="Heatmap of Commit Frequency by Hour of Day and Day of Week",
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    xaxis_nticks=24,  # Ensure 24 tick marks on x-axis (one for each hour)
    yaxis_nticks=7,  # Ensure 7 tick marks on y-axis (one for each day)
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E",  # Dark Gray Background
    paper_bgcolor="#22272E",  # Dark Gray Paper Background
    xaxis=dict(tickfont=dict(color="white")),  # White font for x-axis labels
    yaxis=dict(tickfont=dict(color="white")),  # White font for y-axis labels
    coloraxis_colorbar=dict(
        tickfont=dict(color="white")
    ),  # White font for colorbar labels
)

# Save the generated heatmap to a file
os.makedirs("DataVisuals", exist_ok=True)
fig.write_image("DataVisuals/commit_heatmap.png", width=1200, height=800)
print("Commit heatmap generated successfully.")
