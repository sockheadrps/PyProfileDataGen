import json
import pandas as pd
import plotly.express as px

with open("repo_data.json", "r") as file:
    commit_counts = pd.DataFrame(json.load(file))


def hour_to_am_pm(hour):
    return f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"


commit_counts["HourOfDay"] = commit_counts["HourOfDay"].apply(hour_to_am_pm)

heatmap_data = commit_counts.pivot(index="DayOfWeek", columns="HourOfDay", values="Count").fillna(0)

ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data = heatmap_data.reindex(ordered_days)
hours_order = [f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}" for hour in range(24)]

# Reorder columns according to hours_order
heatmap_data = heatmap_data.reindex(columns=hours_order)

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Hour of Day", y="Day of Week", color="Commit Count"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    aspect="auto",
)

fig.update_layout(
    title="Heatmap of Commit Frequency by Hour of Day and Day of Week",
    xaxis_nticks=24,
    yaxis_nticks=7,
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E",  # Set plot background color
    paper_bgcolor="#22272E",  # Set entire figure background color
    xaxis=dict(tickfont=dict(color="white")),  # Set x-axis tick font color
    yaxis=dict(tickfont=dict(color="white")),  # Set y-axis tick font color
    coloraxis_colorbar=dict(tickfont=dict(color="white")),  # Set colorbar tick font color
)

fig.write_image("DataVisuals/commit_heatmap.png")
