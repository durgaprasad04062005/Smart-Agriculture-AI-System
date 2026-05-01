/**
 * Dashboard.jsx
 * Analytics dashboard showing crop distribution, weather trends,
 * soil vs yield charts, and model metadata.
 */
import React, { useEffect, useState } from "react";
import { getSampleData, getModelMeta } from "../api";
import { BarChart, PieChart, LineChart } from "./Charts";

// Generate mock weather trend data for visualization
function mockWeatherTrend() {
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return {
    labels: months,
    temp:   months.map((_, i) => 18 + 10 * Math.sin((i / 11) * Math.PI) + Math.random() * 2),
    hum:    months.map((_, i) => 55 + 25 * Math.sin(((i + 3) / 11) * Math.PI) + Math.random() * 5),
    rain:   months.map((_, i) => Math.max(0, 80 + 120 * Math.sin(((i + 4) / 11) * Math.PI) + Math.random() * 20)),
  };
}

export default function Dashboard() {
  const [sampleData, setSampleData] = useState(null);
  const [meta, setMeta]             = useState(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const weather                     = mockWeatherTrend();

  useEffect(() => {
    Promise.all([getSampleData(), getModelMeta()])
      .then(([sd, m]) => { setSampleData(sd); setMeta(m); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ textAlign: "center", padding: 60, color: "var(--text-muted)" }}>
      <div className="spinner" style={{ width: 32, height: 32, borderColor: "var(--green-light)", borderTopColor: "var(--green-dark)", margin: "0 auto 12px" }} />
      Loading dashboard data…
    </div>
  );

  if (error) return (
    <div className="alert alert-error">
      ⚠️ Could not load dashboard: {error}. Make sure the backend is running and the model is trained.
    </div>
  );

  // Prepare crop distribution data
  const cropCounts = sampleData?.crop_counts || {};
  const topCrops   = Object.entries(cropCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* ── Model stats ──────────────────────────────────────────────────────── */}
      {meta && (
        <div className="grid-3">
          <div className="stat-card">
            <div className="stat-value">{(meta.accuracy * 100).toFixed(1)}%</div>
            <div className="stat-label">Model Accuracy</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{meta.crops?.length || 24}</div>
            <div className="stat-label">Supported Crops</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{sampleData?.total_rows?.toLocaleString() || "—"}</div>
            <div className="stat-label">Training Samples</div>
          </div>
        </div>
      )}

      {/* ── Crop distribution ────────────────────────────────────────────────── */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">🌾 Top 10 Crops in Dataset</div>
          <BarChart
            labels={topCrops.map(([c]) => c)}
            values={topCrops.map(([, v]) => v)}
            title="Samples"
          />
        </div>
        <div className="card">
          <div className="card-title">🥧 Crop Distribution</div>
          <PieChart
            labels={topCrops.map(([c]) => c)}
            values={topCrops.map(([, v]) => v)}
          />
        </div>
      </div>

      {/* ── Weather trends ───────────────────────────────────────────────────── */}
      <div className="card">
        <div className="card-title">🌤️ Simulated Weather Trends (Annual)</div>
        <LineChart
          labels={weather.labels}
          datasets={[
            { label: "Temperature (°C)", data: weather.temp.map((v) => +v.toFixed(1)) },
            { label: "Humidity (%)",     data: weather.hum.map((v)  => +v.toFixed(1)) },
          ]}
        />
      </div>

      <div className="card">
        <div className="card-title">🌧️ Monthly Rainfall (mm)</div>
        <BarChart
          labels={weather.labels}
          values={weather.rain.map((v) => +v.toFixed(1))}
          title="Rainfall (mm)"
        />
      </div>

      {/* ── Dataset stats ────────────────────────────────────────────────────── */}
      {sampleData?.stats && (
        <div className="card">
          <div className="card-title">📊 Dataset Statistics</div>
          <div style={{ overflowX: "auto" }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>Min</th>
                  <th>Mean</th>
                  <th>Max</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(sampleData.stats).map(([col, s]) => (
                  <tr key={col}>
                    <td><strong>{col}</strong></td>
                    <td>{s.min}</td>
                    <td>{s.mean}</td>
                    <td>{s.max}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Feature importance ───────────────────────────────────────────────── */}
      {meta?.feature_importance && (
        <div className="card">
          <div className="card-title">🔍 Global Feature Importance</div>
          <BarChart
            labels={Object.keys(meta.feature_importance)}
            values={Object.values(meta.feature_importance).map((v) => +(v * 100).toFixed(2))}
            title="Importance (%)"
            horizontal
          />
        </div>
      )}
    </div>
  );
}
