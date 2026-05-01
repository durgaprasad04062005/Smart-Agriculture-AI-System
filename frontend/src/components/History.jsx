/**
 * History.jsx
 * Shows the last 20 predictions made in this session.
 */
import React, { useEffect, useState } from "react";
import { getHistory } from "../api";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const load = () => {
    setLoading(true);
    getHistory()
      .then((d) => setHistory(d.history || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) return (
    <div style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
      Loading history…
    </div>
  );

  if (error) return (
    <div className="alert alert-error">⚠️ {error}</div>
  );

  if (history.length === 0) return (
    <div className="alert alert-info">
      📋 No predictions yet. Go to the <strong>Predict</strong> tab and run your first analysis!
    </div>
  );

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 0 }}>📋 Prediction History</div>
        <button className="btn btn-secondary" style={{ padding: "6px 14px", fontSize: "0.85rem" }} onClick={load}>
          🔄 Refresh
        </button>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table className="history-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Time</th>
              <th>Crop</th>
              <th>Confidence</th>
              <th>Yield (t/ha)</th>
              <th>Temp (°C)</th>
              <th>Humidity (%)</th>
              <th>Rainfall (mm)</th>
              <th>Soil</th>
            </tr>
          </thead>
          <tbody>
            {[...history].reverse().map((entry) => (
              <tr key={entry.id}>
                <td style={{ color: "var(--text-muted)" }}>{entry.id}</td>
                <td style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </td>
                <td><span className="crop-pill">{entry.output.crop}</span></td>
                <td>
                  <span style={{
                    color: entry.output.confidence >= 0.8 ? "var(--green-mid)"
                         : entry.output.confidence >= 0.5 ? "var(--amber)"
                         : "var(--red)",
                    fontWeight: 600,
                  }}>
                    {entry.output.confidence_pct}
                  </span>
                </td>
                <td>{entry.output.expected_yield}</td>
                <td>{entry.input.temperature}</td>
                <td>{entry.input.humidity}</td>
                <td>{entry.input.rainfall}</td>
                <td style={{ textTransform: "capitalize" }}>{entry.input.soil_type || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
