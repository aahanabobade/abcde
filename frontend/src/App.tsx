import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import './App.css'

type Point = { time: string; actual: number; forecast: number; error: number }
type Metrics = {
  n: number; mae: number; rmse: number; bias: number
  p50_abs: number; p90_abs: number; p99_abs: number
}

function nextDay(d: string) {
  const dt = new Date(d + 'T00:00:00Z')
  dt.setUTCDate(dt.getUTCDate() + 1)
  return dt.toISOString().slice(0, 10)
}

export default function App() {
  const [start, setStart] = useState('2026-01-01')
  const [end, setEnd] = useState('2026-01-07')
  const [horizon, setHorizon] = useState(24)
  const [series, setSeries] = useState<Point[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [error, setError] = useState('')
  const [byHorizon, setByHorizon] = useState<
    { horizon: number; mae: number; p90_abs: number }[]
  >([])

  useEffect(() => {
    const q = `start=${start}&end=${nextDay(end)}&horizon=${horizon}`
    setError('')
    fetch(`/api/error-by-horizon?start=${start}&end=${nextDay(end)}`)
      .then(r => r.json())
      .then(setByHorizon)
      .catch(() => {})
    Promise.all([
      fetch(`/api/series?${q}`).then(r => r.json()),
      fetch(`/api/metrics?${q}`).then(r => r.json()),
    ])
      .then(([s, m]) => { setSeries(s); setMetrics(m) })
      .catch(() => setError('Could not reach the backend'))
  }, [start, end, horizon])

  const cards: [string, number | undefined, string][] = [
    ['MAE', metrics?.mae, 'MW'],
    ['RMSE', metrics?.rmse, 'MW'],
    ['Bias (forecast − actual)', metrics?.bias, 'MW'],
    ['90th pct abs error', metrics?.p90_abs, 'MW'],
    ['Points compared', metrics?.n, ''],
  ]

  return (
    <>
      <div className="header">
        <div className="header-inner">
          <h1>UK Wind Forecast Monitor</h1>
          <p>Actual vs. the latest forecast available {horizon}h before each target time (UTC).</p>
        </div>
      </div>

      <div className="app">
        <div className="controls">
          <label>From
            <input type="date" min="2026-01-01" max="2026-01-31" value={start}
              onChange={e => setStart(e.target.value)} />
          </label>
          <label>To
            <input type="date" min="2026-01-01" max="2026-01-31" value={end}
              onChange={e => setEnd(e.target.value)} />
          </label>
          <label>Forecast horizon: {horizon}h
            <input type="range" min={0} max={48} step={1} value={horizon}
              onChange={e => setHorizon(Number(e.target.value))} />
          </label>
        </div>

        {error && <p style={{ color: 'crimson' }}>{error}</p>}

        <div className="cards">
          {cards.map(([label, value, unit]) => {
            const tone = label.startsWith('Bias')
              ? ((value ?? 0) > 0 ? 'bad' : 'good')
              : ''
            return (
              <div className={`card ${tone}`} key={label}>
                <div className="label">{label}</div>
                <div className="value">
                  {value === undefined ? '–' : Math.round(value).toLocaleString()} {unit}
                </div>
              </div>
            )
          })}
        </div>

        <div className="chart">
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={series} margin={{ top: 20, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" minTickGap={60}
                tickFormatter={t => String(t).slice(5, 16).replace('T', ' ')} />
              <YAxis unit=" MW" width={80} />
              <Tooltip labelFormatter={t => String(t).slice(0, 16).replace('T', ' ') + ' UTC'} />
              <Legend />
              <Line type="monotone" dataKey="actual" stroke="#16a34a" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="forecast" stroke="#dc2626" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <h2>Forecast error by horizon</h2>
        <p>How wrong forecasts are depending on how many hours ahead they were published.</p>
        <div className="chart">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byHorizon} margin={{ top: 20, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="horizon" unit="h" />
              <YAxis unit=" MW" width={80} />
              <Tooltip formatter={(v) => Math.round(Number(v)) + ' MW'} />
              <Legend />
              <Bar dataKey="mae" name="MAE" fill="#16a34a" />
              <Bar dataKey="p90_abs" name="90th pct abs error" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  )
}