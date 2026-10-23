from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FMT = "%Y-%m-%dT%H:%MZ"


def fetch_range(dataset, start, end, extra=None):
    rows, day = [], start
    while day < end:
        nxt = min(day + timedelta(days=1), end)
        params = {"publishDateTimeFrom": day.strftime(FMT),
                  "publishDateTimeTo": nxt.strftime(FMT)}
        params.update(extra or {})
        r = requests.get(f"{BASE}/{dataset}/stream", params=params, timeout=60)
        r.raise_for_status()
        rows.extend(r.json())
        print(f"{dataset} {day:%Y-%m-%d}: {len(r.json())} rows")
        day = nxt
    return pd.DataFrame(rows)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    utc = timezone.utc
    # Actuals for January 2026 targets
    actuals = fetch_range("FUELHH", datetime(2026, 1, 1, tzinfo=utc),
                          datetime(2026, 2, 1, tzinfo=utc), {"fuelType": "WIND"})
    actuals = actuals[actuals["fuelType"] == "WIND"]
    actuals = actuals[["startTime", "generation"]].drop_duplicates("startTime")
    actuals.to_csv(DATA_DIR / "actuals.csv", index=False)

    # Forecasts published from late Dec (for early Jan targets) to end of Jan
    fc = fetch_range("WINDFOR", datetime(2025, 12, 28, tzinfo=utc),
                     datetime(2026, 2, 1, tzinfo=utc))
    fc = fc[["startTime", "publishTime", "generation"]]
    fc.to_csv(DATA_DIR / "forecasts.csv", index=False)
    print("Done:", len(actuals), "actual rows,", len(fc), "forecast rows")


if __name__ == "__main__":
    main()