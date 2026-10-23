# UK Wind Forecast Monitor

Web app for comparing national wind generation **forecasts** (Elexon WINDFOR) against **actuals** (Elexon FUELHH, fuel type WIND) for January 2026, to support day-ahead power purchase decisions.

**Live app:** https://abcde-virid.vercel.app

## What it does
- For each target half-hour, shows the **latest forecast available `N` hours before** the target (the forecast a buyer could actually see), where `N` is the horizon slider (0 to 48h).
- Compares it against actual generation: MAE, RMSE, bias (forecast − actual), 90th percentile absolute error.
- Shows how error grows with forecast horizon.
- All times are UTC. WINDFOR is hourly, so only hourly points can be compared.

## Files and directories
```
backend/
  ingest.py        Downloads FUELHH and WINDFOR data from Elexon into data/
  analysis.py      Forecast selection and error metrics (pandas)
  main.py          FastAPI app: /api/series, /api/metrics, /api/error-by-horizon
  requirements.txt Python dependencies
frontend/          React + TypeScript (Vite) dashboard, charts with Recharts
data/              actuals.csv, forecasts.csv (downloaded Elexon data)
public/            Built frontend served on Vercel
index.py           Vercel entry point (imports the FastAPI app)
vercel.json        Vercel configuration
requirements.txt   Minimal dependencies used by the Vercel deployment
Dockerfile         Builds the frontend and serves everything from one container
```

## How to start

### With Docker
```bash
docker build -t wind-monitor .
docker run -p 8000:8000 wind-monitor
```
Open http://localhost:8000

### Without Docker
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 (the dev server proxies `/api` to port 8000).

### Refresh the data (optional)
```bash
cd backend && python ingest.py
```

## Deployment
Deployed on Vercel as a single FastAPI service (`vercel.json`). The built frontend is committed in `public/` and served as static files; Docker is used for local and portable runs.

## AI tools
AI assistance (Claude) was used to help build this application.