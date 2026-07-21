import pandas as pd

merged = pd.read_csv("data/merged_features.csv", index_col=0, parse_dates=True)

print("Total rows:", len(merged))
print("Rows with news_count_lag1 > 0:", (merged["news_count_lag1"] > 0).sum())
print("Rows with news_count_lag1 == 0:", (merged["news_count_lag1"] == 0).sum())

print("\nSample from 2020:")
print(merged.loc["2020-01-01":"2020-01-15", ["Close", "news_count_lag1"]])

print("\nSample from 2023:")
print(merged.loc["2023-01-01":"2023-01-15", ["Close", "news_count_lag1"]])