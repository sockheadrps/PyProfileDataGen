import json
import re
from collections import Counter
import plotly.express as px
from wordcloud import WordCloud
import numpy as np
from PIL import Image

# Load repository data from a JSON file
with open("repo_data.json", "r") as json_file:
    repo_data: dict[str, list] = json.load(json_file)

# Extract all commit messages from the repository data
all_commit_messages: str = " ".join(
    message
    for repo in repo_data["repo_stats"]
    for message in repo.get("commit_messages", [])
)

# Process the commit messages to remove non-alphabetical characters and convert to lowercase
processed_text: str = re.sub(r"[^a-zA-Z\s]", "", all_commit_messages).lower()

# Define a set of words to ignore in the word cloud
ignore_words: set[str] = {
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

# Count the occurrences of each word, excluding ignored words
word_counts: Counter[str] = Counter(
    word for word in processed_text.split() if word not in ignore_words
)

# Get the top 60 most common words
top_60_words: dict[str, int] = dict(word_counts.most_common(60))

# Define a list of pastel colors for the word cloud
pastel_colors: list[str] = [
    "#f8d7da",  # Pastel red
    "#d4edda",  # Pastel green
    "#d1ecf1",  # Pastel blue
    "#fff3cd",  # Pastel yellow
    "#f8d7da",  # Pastel pink
    "#e2e0eb",  # Pastel purple
]


def color_func(word: str, **kwargs) -> str:
    """
    Randomly select a color for a word from the pastel color list.

    Args:
    - word (str): The word being colored (not used in this function).
    - kwargs: Additional keyword arguments (not used in this function).

    Returns:
    - str: A hex color code chosen randomly from the pastel color list.
    """
    return np.random.choice(pastel_colors)


# Generate a word cloud image from the top 60 words
wordcloud: WordCloud = WordCloud(
    width=800,
    height=400,
    background_color="#22272E",
    color_func=color_func,
).generate_from_frequencies(top_60_words)

# Convert the word cloud to a NumPy array (image)
wordcloud_image: np.ndarray = np.array(wordcloud)

# Create a Plotly figure to display the word cloud image
fig = px.imshow(wordcloud_image)

# Update the layout of the figure
fig.update_layout(
    font=dict(family="Arial, sans-serif", size=14, color="rgb(255, 255, 255)"),
    title="Top 60 Words in Commit Messages Word Cloud",
    xaxis={"visible": False},
    yaxis={"visible": False},
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor="#22272E",
    paper_bgcolor="#22272E",
)

# Save the word cloud image to a file
fig.write_image("DataVisuals/wordcloud.png", width=1200, height=800)

print("Word cloud image created and saved successfully.")
