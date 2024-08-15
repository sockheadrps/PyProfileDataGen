import json
import pandas as pd
import plotly.express as px
import os



with open("repo_data.json", "r") as file:
    data = json.load(file)

# Flatten the commit_counts structure from the JSON
commit_data = []
for day, hours in data["commit_counts"].items():
    for hour, count in hours.items():
        commit_data.append({"DayOfWeek": day, "HourOfDay": int(hour), "Count": count})

commit_counts = pd.DataFrame(commit_data)

def hour_to_am_pm(hour):
    return f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"

commit_counts["HourOfDay"] = commit_counts["HourOfDay"].apply(hour_to_am_pm)

heatmap_data = commit_counts.pivot(index="DayOfWeek", columns="HourOfDay", values="Count").fillna(0)

# Ensure days are ordered properly
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data = heatmap_data.reindex(ordered_days)

# Ensure hours are ordered properly
hours_order = [f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}" for hour in range(24)]
heatmap_data = heatmap_data.reindex(columns=hours_order)

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Hour of Day", y="Day of Week", color="Commit Count"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    aspect="auto",
    color_continuous_scale="Plasma",
    zmin=0,
    zmax=heatmap_data.max().max(),
)

fig.update_layout(
    title="Heatmap of Commit Frequency by Hour of Day and Day of Week",
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    xaxis_nticks=24,
    yaxis_nticks=7,
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
    xaxis=dict(tickfont=dict(color="white")),
    yaxis=dict(tickfont=dict(color="white")),
    coloraxis_colorbar=dict(tickfont=dict(color="white")),
)

# Save the figure
os.makedirs("DataVisuals", exist_ok=True)
fig.write_image("DataVisuals/commit_heatmap.png", width=1200, height=800)
print("Commit heatmap generated successfully.")
