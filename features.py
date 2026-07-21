import yfinance as yf
import pandas as pd
import json
import time

ticker = "USO"

# --- Step 1: Download price data year-by-year, with retries ---
years = range(2015, 2026)
chunks = []

for year in years:
    start = f"{year}-01-01"
    end = f"{year+1}-01-01"

    df_year = pd.DataFrame()
    for attempt in range(3):
        print(f"Fetching {ticker} {start} -> {end} (attempt {attempt+1})")
        df_year = yf.download(ticker, start=start, end=end, auto_adjust=False)
        if not df_year.empty:
            break
        print(f"  -> empty, retrying in 5s...")
        time.sleep(5)

    if not df_year.empty:
        chunks.append(df_year)
    else:
        print(f"  -> FINAL: No data for {year} after 3 attempts")

df = pd.concat(chunks)
df = df[~df.index.duplicated(keep="first")]
df = df.sort_index()

print("\nCombined shape:", df.shape)
df.to_csv("data/price_raw.csv")
print("raw price downloaded:")
print(df.head())

# --- Step 2: Process price features ---
price = df.copy()
price.columns = price.columns.get_level_values(0)
price = price[["Open", "High", "Low", "Close", "Volume"]]

price["return"] = price["Close"].pct_change()
price["target"] = (price["Close"].shift(-1) > price["Close"]).astype(int)
# Volatility target: was tomorrow's move unusually large (regardless of direction)?
price["next_day_abs_return"] = abs(price["Close"].shift(-1) / price["Close"] - 1)

# Threshold = median absolute daily move across the dataset
threshold = price["next_day_abs_return"].median()
price["target_vol"] = (price["next_day_abs_return"] > threshold).astype(int)

print(f"\nVolatility threshold (median abs return): {threshold:.4f}")
print(price["target_vol"].value_counts())
price = price.dropna()

print("\nProcessed price features:")
print(price.head())

price.to_csv("data/price_features.csv")
print("\nProcessed price data:")
print(price.head())

# --- Step 3: Load GDELT news data ---
# Load the daily sentiment features
# --- Step 3: Load GDELT daily sentiment data ---

# Load the daily sentiment features
sentiment = pd.read_csv(
    "data/daily_sentiment.csv",
    index_col=0,
    parse_dates=True
)

print("\nDaily sentiment data:")
print(sentiment.head())

# Create a lagged version of article count
# Yesterday's news count will be used to predict today's movement
sentiment["news_count_lag1"] = sentiment["article_count"].shift(1)

# Merge ONLY lagged features with the price data
merged = price.join(
    sentiment[
        [
            "news_count_lag1",
            "sentiment_sum_lag1",
            "sentiment_mean_lag1"
        ]
    ],
    how="left"
)

# Fill missing values (days with no previous news)
merged["news_count_lag1"] = merged["news_count_lag1"].fillna(0)
merged["sentiment_sum_lag1"] = merged["sentiment_sum_lag1"].fillna(0)
merged["sentiment_mean_lag1"] = merged["sentiment_mean_lag1"].fillna(0)

# Save the final merged dataset
print("\nColumns in merged dataset:")
print(merged.columns)

merged.to_csv("data/merged_features.csv")

print("\nMerged dataset:")
print(merged.head())

print("\nTotal rows:", len(merged))