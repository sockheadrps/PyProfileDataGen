import json, re, ast, configparser
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config_helper import config

# -------- config helpers --------
def load_ignored_words_from_config():

    # Base set: very light stopwords so we don't nuke everything
    base = {
        "the","and","to","in","of","on","a","an","for","is","it","this","that","with","from","by"
    }

    # Optional section: [WordCloud] ignored_words = ["initial","commit","update","readme", ...]
    extra = set()
    if config.has_section("WordCloud") and config.has_option("WordCloud", "ignored_words"):
        raw = config.get("WordCloud", "ignored_words", fallback="[]").strip()
        try:
            # allow JSON/TOML-like lists: ["foo","bar"]
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, (list, tuple, set)):
                extra = {str(x).lower().strip() for x in parsed}
        except Exception:
            # also accept comma-separated fallback
            extra = {w.strip().lower() for w in raw.split(",") if w.strip()}

    return base | extra

# -------- load repo_data --------
with open("repo_data.json", "r", encoding="utf-8") as f:
    repo_data = json.load(f)

if not repo_data.get("repo_stats"):
    print("❌ No repository data found. Please run data_scrape.py first.")
    raise SystemExit(0)  # don't fail the job—just skip

# Prefer recent_commits → fallback to per-repo commit_messages
if repo_data.get("recent_commits"):
    all_commit_messages = " ".join(commit.get("message", "") for commit in repo_data["recent_commits"])
else:
    all_commit_messages = " ".join(
        msg for repo in repo_data["repo_stats"] for msg in repo.get("commit_messages", [])
    )

if not all_commit_messages.strip():
    print("⚠ No commit messages found. Writing placeholder word cloud.")
    img = Image.new("RGB", (1200, 800), color="#22272E")
    ImageDraw.Draw(img).text((40, 40), "No commit messages found", fill=(255, 255, 255))
    Path("DataVisuals").mkdir(parents=True, exist_ok=True)
    img.save("DataVisuals/wordcloud.png")
    raise SystemExit(0)

print(f"📝 Found {len(all_commit_messages.split())} raw words")

# -------- processing --------
processed_text = re.sub(r"[^a-zA-Z\s]", " ", all_commit_messages).lower()
tokens = [t for t in processed_text.split() if t]

# Start with config-driven ignore list
ignored = load_ignored_words_from_config()

def count_words(ignored_set):
    return Counter(w for w in tokens if w not in ignored_set and len(w) > 1)

word_counts = count_words(ignored)

# If we filtered too hard, relax the ignore list to a minimal stoplist
if not word_counts:
    print("ℹ Filter too strict; relaxing ignore list.")
    minimal = {"the","and","to","in","of","on","a","an"}
    word_counts = count_words(minimal)

# Still nothing? Write a placeholder and exit gracefully.
if not word_counts:
    print("⚠ No words after filtering; writing placeholder.")
    img = Image.new("RGB", (1200, 800), color="#22272E")
    ImageDraw.Draw(img).text((40, 40), "Not enough meaningful words for a word cloud", fill=(255, 255, 255))
    Path("DataVisuals").mkdir(parents=True, exist_ok=True)
    img.save("DataVisuals/wordcloud.png")
    raise SystemExit(0)

top_60 = dict(word_counts.most_common(60))
print(f"🔤 Using {len(top_60)} words. Top: '{max(word_counts, key=word_counts.get)}'")

# -------- word cloud --------
pastel_colors = ["#f8d7da","#d4edda","#d1ecf1","#fff3cd","#f8d7da","#e2e0eb"]
def color_func(word, **kwargs): return np.random.choice(pastel_colors)

wc = WordCloud(
    width=800, height=400, background_color="#22272E", color_func=color_func
).generate_from_frequencies(top_60)

img_arr = np.array(wc)
fig = px.imshow(img_arr)
fig.update_layout(
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255,255,255)"),
    title="Top Words in Commit Messages",
    xaxis={"visible": False}, yaxis={"visible": False},
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E", paper_bgcolor="#22272E",
)

Path("DataVisuals").mkdir(parents=True, exist_ok=True)
fig.write_image("DataVisuals/wordcloud.png", width=1200, height=800)
print("✅ Word cloud image created.")
