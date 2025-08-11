import json
import plotly.express as px
import pandas as pd
import sys, os, math
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config_helper import config  # user's config.ini

GENERATE = config.getboolean("Settings", "generate_merged_prs", fallback=True)

# --- theme ---
BG = "#0d1117"
GRID = "rgba(255,255,255,0.08)"
AXIS = "rgba(255,255,255,0.20)"
TEXT = "#ffffff"
ACCENT = config.get("Theme", "accent_color", fallback="#58a6ff")

def wrap_text(s: str, width: int = 60) -> str:
    """Insert <br> breaks to wrap long text nicely on the y-axis."""
    s = (s or "").strip()
    if len(s) <= width:
        return s
    parts, line = [], []
    for word in s.split():
        if sum(len(w) for w in line) + len(line) + len(word) <= width:
            line.append(word)
        else:
            parts.append(" ".join(line))
            line = [word]
    if line:
        parts.append(" ".join(line))
    return "<br>".join(parts)

def safe_int(x):
    try: return int(x)
    except: return 0

# --- load ---
try:
    with open("repo_data.json", "r", encoding="utf-8") as f:
        repo_data = json.load(f)
except FileNotFoundError:
    print("❌ repo_data.json not found. Run mergedprs.py first.")
    raise SystemExit(0)

merged_prs = repo_data.get("merged_prs", [])
if not merged_prs:
    print("⚠ No merged PRs data. Skipping chart.")
    raise SystemExit(0)

rows = []
for pr in merged_prs:
    stars = safe_int(pr.get("stars"))
    title = (pr.get("title") or "").strip()
    repo = pr.get("full_repo_name") or pr.get("repo") or "unknown"
    num = pr.get("number", "")
    closed_raw = pr.get("closed_at") or pr.get("merged_at") or ""
    try:
        closed_dt = datetime.fromisoformat(closed_raw.replace("Z", "+00:00"))
        closed_label = closed_dt.strftime("%b %Y")
    except Exception:
        closed_label = "—"

    label = f"{repo} / #{num}<br>{wrap_text(title, width=58)}"  # <- two-line y-label
    rows.append({
        "Stars": stars,
        "Label": label,
        "Repository": repo,
        "PRNumber": num,
        "Title": title,
        "Closed": closed_label
    })

df = pd.DataFrame(rows).sort_values("Stars", ascending=False).head(10)
if df.empty:
    print("⚠ No PR rows to plot. Skipping.")
    raise SystemExit(0)

# biggest on top (horizontal bars)
df_plot = df.sort_values("Stars", ascending=True)

fig = px.bar(
    df_plot,
    x="Stars",
    y="Label",
    orientation="h",
    text="Stars",
)

fig.update_traces(
    marker_color=ACCENT,
    marker_line_color="rgba(255,255,255,0.15)",
    marker_line_width=1.0,
    texttemplate="%{text}",
    textposition="outside",
    textfont=dict(size=12, color=TEXT),
    hovertemplate="<b>%{y}</b><br>⭐ Stars: %{x}<br>🗓 Closed: %{customdata}<extra></extra>",
    customdata=df_plot["Closed"],
)

xmax = max(10, int(df_plot["Stars"].max()))
# left margin for two-line y-ticks; scale a bit with label length
max_label_len = max(len(r) for r in df["Label"])
left_margin = min(400, 160 + max(0, (max_label_len - 45)) * 3)

fig.update_layout(
    title=dict(
        text="Top Merged Pull Requests by Repository Stars",
        x=0.5, xanchor="center",
        font=dict(size=22, color=TEXT),
    ),
    font=dict(family="Inter, Arial, sans-serif", size=14, color=TEXT),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    margin=dict(l=left_margin, r=60, t=70, b=40),
    xaxis=dict(
        title="Stars",
        range=[0, xmax * 1.18],
        showgrid=True, gridcolor=GRID,
        zeroline=False,
        showline=True, linecolor=AXIS,
        ticks="outside", tickcolor=AXIS, ticklen=6,
    ),
    yaxis=dict(
        title="",
        showgrid=False,
        zeroline=False,
        showline=True, linecolor=AXIS,
        autorange="reversed",
        tickfont=dict(size=12, color=TEXT),
    ),
)

if GENERATE:
    os.makedirs("DataVisuals", exist_ok=True)
    fig.write_image("DataVisuals/merged_prs_stars.png", width=1400, height=800)
    print("✅ Merged PRs stars chart generated successfully!")
    top = df.iloc[0]
    print(f"📊 Chart shows top {len(df)} PRs by repository stars")
    print(f"🏆 Top PR repo: {top['Repository']} • Stars: {top['Stars']}")
else:
    print("📊 Merged PRs stars chart generation disabled in config")
