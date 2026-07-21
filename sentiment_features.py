import json
import pandas as pd

# Words that indicate increasing geopolitical tension
ESCALATORY_WORDS = [
    "sanctions", "war", "conflict", "strike", "attack", "embargo",
    "military", "invasion", "crisis", "threat", "tension", "retaliation",
    "blockade", "seizure", "explosion", "missile"
]

# Words that indicate decreasing geopolitical tension
DEESCALATORY_WORDS = [
    "agreement", "talks", "ceasefire", "deal", "peace", "resolution",
    "cooperation", "negotiation", "truce", "diplomacy", "accord", "easing"
]
def score_headline(title):
    title_lower = title.lower()

    esc_count = sum(
        1 for w in ESCALATORY_WORDS
        if w in title_lower
    )

    dee_count = sum(
        1 for w in DEESCALATORY_WORDS
        if w in title_lower
    )

    return esc_count - dee_count
with open("data/gdelt_raw_full.json", "r", encoding="utf-8") as f:
    gdelt_data = json.load(f)

# Extract all articles
articles = gdelt_data["articles"]

# Convert into a DataFrame
news_df = pd.DataFrame(articles)

# Display information
print("Total articles loaded:", len(news_df))
print(news_df.columns)
news_df["sentiment_score"] = news_df["title"].apply(score_headline)

news_df["date"] = pd.to_datetime(news_df["seendate"]).dt.date
news_df["date"] = pd.to_datetime(news_df["date"])

daily_sentiment = news_df.groupby("date").agg(
    article_count=("title", "count"),
    sentiment_sum=("sentiment_score", "sum"),
    sentiment_mean=("sentiment_score", "mean")
)

daily_sentiment["sentiment_sum_lag1"] = daily_sentiment["sentiment_sum"].shift(1)
daily_sentiment["sentiment_mean_lag1"] = daily_sentiment["sentiment_mean"].shift(1)

daily_sentiment.to_csv("data/daily_sentiment.csv")

print(daily_sentiment.head(20))