import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta

def fetch_gdelt(query, start_date, end_date, max_retries=3):
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "startdatetime": start_date,
        "enddatetime": end_date,
        "maxrecords": 250
    }

    for attempt in range(max_retries):
        r = requests.get(url, params=params)

        if r.status_code == 429:
            wait = 10 * (attempt + 1)  # back off longer each retry
            print(f"Rate limited. Waiting {wait}s before retry...")
            time.sleep(wait)
            continue

        r.raise_for_status()
        return r.json()

    raise RuntimeError(f"Failed after {max_retries} retries for {start_date}–{end_date}")
def daterange_weekly(start, end):
    current = start
    while current < end:
        next_week = current + timedelta(days=7)
        yield current, min(next_week, end)
        current = next_week


start = datetime(2017, 1, 1)   # GDELT Doc API only covers 2017 onward
end = datetime(2025, 7, 10)

all_articles = []
query = "oil sanctions"

for week_start, week_end in daterange_weekly(start, end):
    s_str = week_start.strftime("%Y%m%d%H%M%S")
    e_str = week_end.strftime("%Y%m%d%H%M%S")

    try:
        data = fetch_gdelt(query, s_str, e_str)
        articles = data.get("articles", [])
        all_articles.extend(articles)
        print(f"{week_start.date()} -> {week_end.date()}: {len(articles)} articles (total so far: {len(all_articles)})")
    except Exception as e:
        print(f"Failed for {week_start.date()}-{week_end.date()}: {e}")

    # save incrementally in case of crash
    with open("data/gdelt_raw_full.json", "w", encoding="utf-8") as f:
        json.dump({"articles": all_articles}, f, ensure_ascii=False, indent=2)

    time.sleep(5)  # respect rate limit

print("\nDone. Total articles collected:", len(all_articles))