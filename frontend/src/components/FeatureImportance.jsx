/**
 * FeatureImportance.jsx
 * Renders a horizontal bar chart showing which features
 * most influenced the crop recommendation.
 */
import React from "react";

const FEATURE_LABELS = {
  N:           "Nitrogen",
  P:           "Phosphorus",
  K:           "Potassium",
  temperature: "Temperature",
  humidity:    "Humidity",
  ph:          "Soil pH",
  rainfall:    "Rainfall",
};

const FEATURE_COLORS = [
  "#2d8a47", "#4caf50", "#66bb6a", "#81c784",
  "#a5d6a7", "#c8e6c9", "#e8f5e9",
];

export default function FeatureImportance({ importance }) {
  if (!importance || Object.keys(importance).length === 0) return null;

  const entries = Object.entries(importance).sort((a, b) => b[1] - a[1]);
  const maxVal  = entries[0][1];

  return (
    <div>
      <div className="card-title">🔍 Feature Importance</div>
      <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 16 }}>
        How much each factor influenced the recommendation:
      </p>
      {entries.map(([key, val], i) => (
        <div className="importance-row" key={key}>
          <div className="importance-label">
            {FEATURE_LABELS[key] || key}
          </div>
          <div className="importance-bar-bg">
            <div
              className="importance-bar-fill"
              style={{
                width: `${(val / maxVal) * 100}%`,
                background: `linear-gradient(90deg, ${FEATURE_COLORS[i % FEATURE_COLORS.length]}, ${FEATURE_COLORS[(i + 1) % FEATURE_COLORS.length]})`,
              }}
            />
          </div>
          <div className="importance-pct">{(val * 100).toFixed(1)}%</div>
        </div>
      ))}
    </div>
  );
}
