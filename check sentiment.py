import pandas as pd

sentiment = pd.read_csv(
    "data/daily_sentiment.csv",
    index_col=0,
    parse_dates=True
)

print(sentiment.columns)