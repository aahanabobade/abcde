from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import analysis
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Wind Forecast Monitor")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

ACTUALS, FORECASTS = analysis.load()


def _slice(df, start: Optional[str], end: Optional[str]):
    if start:
        df = df[df.startTime >= pd.Timestamp(start, tz="UTC")]
    if end:
        df = df[df.startTime < pd.Timestamp(end, tz="UTC")]
    return df


@app.get("/api/series")
def series(start: Optional[str] = None, end: Optional[str] = None,
           horizon: float = Query(24, ge=0, le=48)):
    """Actual vs the latest forecast the buyer could see `horizon` hours ahead."""
    a = _slice(ACTUALS, start, end)
    df = analysis.compare(a, FORECASTS, horizon).sort_values("startTime")
    return [
        {"time": r.startTime.isoformat(),
         "actual": r.generation_actual,
         "forecast": r.generation_forecast,
         "publishTime": r.publishTime.isoformat(),
         "error": r.error}
        for r in df.itertuples()
    ]


@app.get("/api/metrics")
def metrics(start: Optional[str] = None, end: Optional[str] = None,
            horizon: float = Query(24, ge=0, le=48)):
    a = _slice(ACTUALS, start, end)
    return analysis.metrics(analysis.compare(a, FORECASTS, horizon))


@app.get("/api/error-by-horizon")
def error_by_horizon(start: Optional[str] = None, end: Optional[str] = None):
    a = _slice(ACTUALS, start, end)
    out = []
    for h in range(0, 49, 4):
        m = analysis.metrics(analysis.compare(a, FORECASTS, h))
        out.append({"horizon": h, **m})
    return out


STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")