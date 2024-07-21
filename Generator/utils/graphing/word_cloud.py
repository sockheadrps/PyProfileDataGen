import json
import re
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud

with open("repo_data.json", "r") as json_file:
    repo_data = json.load(json_file)

# Combine all commit messages into a single string
all_commit_messages = " ".join(
    message for repo in repo_data["repo_stats"] for message in repo.get("commit_messages", [])
)

# Remove punctuation and numbers, convert to lowercase
processed_text = re.sub(r"[^a-zA-Z\s]", "", all_commit_messages).lower()

ignore_words = {
    "initial",
    "commit",
    "for",
    "the",
    "and",
    "to",
    "in",
    "of",
    "on",
    "with",
    "from",
    "by",
    "a",
    "an",
    "readme",
    "readmemd",
    "is",
    "python",
    "that",
    "this",
    "some",
    "update",
    "beauxmain",
    "be",
    "into",
    "end",
    "was",
    "made",
}

word_counts = Counter(word for word in processed_text.split() if word not in ignore_words)

top_60_words = dict(word_counts.most_common(60))

for word in top_60_words:
    print(f"{word}: {top_60_words[word]}")

wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(top_60_words)

wordcloud_image = wordcloud.to_image()
wordcloud_image.save("wordcloud.png")


fig = px.imshow(wordcloud_image)

fig.update_layout(
    title="Top 60 Words in Commit Messages Word Cloud",
    xaxis={"visible": False},
    yaxis={"visible": False},
    margin=dict(l=0, r=0, t=30, b=0),  # Reduce margins
)


fig.update_layout(
    title="Top 60 Words in Commit Messages Word Cloud", xaxis={"visible": False}, yaxis={"visible": False}
)

fig.write_image("DataVisuals/wordcloud.png", width=1200, height=800)
