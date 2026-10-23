from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JAN_START = pd.Timestamp("2026-01-01", tz="UTC")
JAN_END = pd.Timestamp("2026-02-01", tz="UTC")


def load():
    a = pd.read_csv(DATA_DIR / "actuals.csv", parse_dates=["startTime"])
    f = pd.read_csv(DATA_DIR / "forecasts.csv",
                    parse_dates=["startTime", "publishTime"])
    a = a[(a.startTime >= JAN_START) & (a.startTime < JAN_END)]
    f = f[(f.startTime >= JAN_START) & (f.startTime < JAN_END)]
    return a, f


def latest_forecast(f, horizon_hours):
    """Per target time, latest forecast published >= horizon_hours before it."""
    f = f.copy()
    f["horizon_h"] = (f.startTime - f.publishTime).dt.total_seconds() / 3600
    ok = f[f.horizon_h >= horizon_hours]
    return ok.sort_values("publishTime").groupby("startTime").tail(1)


def compare(a, f, horizon_hours):
    fc = latest_forecast(f, horizon_hours)
    df = a.merge(fc, on="startTime", suffixes=("_actual", "_forecast"))
    df["error"] = df.generation_forecast - df.generation_actual
    return df


def metrics(df):
    err = df["error"]
    return {
        "n": int(len(df)),
        "mae": float(err.abs().mean()),
        "rmse": float((err ** 2).mean() ** 0.5),
        "bias": float(err.mean()),
        "p50_abs": float(err.abs().quantile(0.5)),
        "p90_abs": float(err.abs().quantile(0.9)),
        "p99_abs": float(err.abs().quantile(0.99)),
    }


if __name__ == "__main__":
    a, f = load()
    for h in (1, 6, 12, 24, 36, 48):
        print(h, metrics(compare(a, f, h)))