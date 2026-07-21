\# Geopolitical News-Driven Stock Predictor



A machine learning pipeline that tests whether geopolitical news signals (volume and sentiment)

can predict short-term price movement or volatility in an oil-sensitive ETF (USO).



\## Motivation



Markets are widely believed to be highly efficient at pricing in public information almost

instantly. This project set out to rigorously test that assumption on a narrow, well-defined

hypothesis: does daily geopolitical news activity around "oil sanctions" help predict next-day

USO price direction or volatility?



\## Pipeline Overview



1\. \*\*Price data\*\* — Daily OHLCV data for USO (2015–2025), pulled via `yfinance`, fetched in

&#x20;  yearly chunks with retry logic to handle intermittent API failures.

2\. \*\*News data\*\* — \~56,750 articles from the GDELT Doc API (2017–2025, GDELT's earliest

&#x20;  coverage), collected via a rate-limited, resumable weekly-chunk loop querying "oil sanctions".

3\. \*\*Feature engineering\*\*:

&#x20;  - Daily article count

&#x20;  - Keyword-based sentiment scoring (escalatory vs. de-escalatory word counts per headline)

&#x20;  - All news features lagged by 1 day to prevent lookahead bias

4\. \*\*Modeling\*\* — Random Forest classifier, trained on a chronological 80/20 split (no random

&#x20;  shuffling, to respect time-series ordering).

5\. \*\*Targets tested\*\*:

&#x20;  - Next-day price direction (up/down)

&#x20;  - Next-day volatility (whether the absolute price move exceeds the historical median)



\## Key Design Decisions



\- \*\*Chronological train/test split\*\* — critical for time-series data; random shuffling would

&#x20; leak future information into training.

\- \*\*1-day feature lag\*\* — ensures the model only ever uses information that would have been

&#x20; available before the prediction point.

\- \*\*Yearly-chunked, retry-wrapped data fetching\*\* — both Yahoo Finance and GDELT had intermittent

&#x20; failures on large date ranges; chunking + retries made the pipeline reliable.

\- \*\*Resumable GDELT collection\*\* — the \~450-week historical pull (40–60 min runtime) saves

&#x20; progress incrementally, so it can be safely interrupted and resumed.



\## Results



| Feature Set                          | Target      | Accuracy |

|---------------------------------------|-------------|----------|

| Price features only                   | Direction   | 53.3%    |

| Price + news count                    | Direction   | 53.3% (news feature had lowest importance) |

| News count + return only              | Direction   | 47.6%    |

| News count + sentiment + return       | Direction   | 47.9%    |

| News count + sentiment + return       | Volatility  | 48.6%    |



Across every feature combination tested, geopolitical news features (raw count and

keyword-based sentiment) showed \*\*low feature importance and did not improve accuracy above

chance level\*\*. `return` consistently dominated feature importance regardless of what else was

included.



\## Interpretation



This is a genuine, consistent null result, not a pipeline failure. Likely explanations:



\- \*\*Market efficiency\*\* — public news is priced in quickly, especially for a liquid, well-covered

&#x20; instrument like USO.

\- \*\*Weak feature proxy\*\* — a keyword-count sentiment score is a coarse measure of geopolitical

&#x20; significance; it can't distinguish a minor procedural headline from a major escalation.

\- \*\*Lag mismatch\*\* — a 1-day lag may not match the actual speed at which oil markets digest

&#x20; geopolitical developments.

\- \*\*Query narrowness\*\* — a single fixed query ("oil sanctions") likely misses relevant events

&#x20; described in other language.



\## Known Limitations



\- The volatility threshold was computed using the full dataset's median, which introduces mild

&#x20; lookahead bias. A more rigorous version would compute the threshold from training data only.

\- GDELT's Doc API only covers 2017 onward; 2015–2016 price data has no matching news features.

\- Sentiment scoring uses a small, manually defined keyword list rather than a trained NLP model.



\## Next Steps



\- Compute the volatility threshold using only the training set

\- Try longer/rolling lag windows (3-day, 5-day aggregates) instead of a single 1-day lag

\- Replace keyword-based sentiment with a proper NLP sentiment model (e.g., FinBERT)

\- Test multiple, separate geopolitical query categories (e.g., OPEC, conflict, trade policy)

&#x20; instead of one combined query

\- Try gradient boosting (XGBoost/LightGBM) as an alternative to Random Forest

\- Predict continuous volatility magnitude (regression) instead of a binary threshold



\## Tech Stack



\- Python, pandas, scikit-learn

\- yfinance (price data)

\- GDELT Doc API (geopolitical news data)



\## Project Structure



\\`\\`\\`

stock-predictor/

&#x20; data/                     # generated datasets (not committed — see .gitignore)

&#x20; gdelt.py                  # historical GDELT news collection (resumable, rate-limited)

&#x20; features.py                # price + news + sentiment feature pipeline

&#x20; sentiment\_features.py      # keyword-based sentiment scoring

&#x20; model.py                   # model training and evaluation

&#x20; check\_data.py               # data validation / sanity checks

&#x20; README.md

\\`\\`\\`

