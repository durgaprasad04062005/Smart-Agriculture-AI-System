/**
 * ResultCard.jsx — Crop recommendation result with profit breakdown
 */
import React, { useState } from "react";

const CROP_EMOJIS = {
  rice:"🌾",maize:"🌽",wheat:"🌾",cotton:"🌿",sugarcane:"🎋",
  coffee:"☕",jute:"🌿",coconut:"🥥",banana:"🍌",mango:"🥭",
  grapes:"🍇",apple:"🍎",orange:"🍊",papaya:"🍈",watermelon:"🍉",
  muskmelon:"🍈",pomegranate:"🍎",chickpea:"🫘",kidneybeans:"🫘",
  lentil:"🫘",blackgram:"🫘",mungbean:"🫘",mothbeans:"🫘",pigeonpeas:"🫘",
};

export default function ResultCard({ result }) {
  const [showCosts, setShowCosts] = useState(false);
  if (!result) return null;

  const emoji  = CROP_EMOJIS[result.crop] || "🌱";
  const profit = result.profit;
  const confPct = result.confidence * 100;
  const confColor = confPct >= 80 ? "#52b788" : confPct >= 50 ? "#fbbf24" : "#dc2626";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* ── Crop hero ──────────────────────────────────────────────────── */}
      <div className="result-hero">
        <div className="result-crop-emoji">{emoji}</div>
        <div className="result-crop-name">{result.crop}</div>
        <div className="result-confidence-badge" style={{ background: confColor + "33", borderColor: confColor }}>
          {result.confidence_pct} confidence
        </div>
        <div style={{ fontSize: ".9rem", opacity: .8, marginTop: 4 }}>
          Expected Yield: <strong>{result.expected_yield} t/ha</strong>
          {result.profit?.hectares > 1 && ` × ${result.profit.hectares} ha = ${result.profit.total_yield_t}t total`}
        </div>
        <div className="result-explanation">
          💡 <strong>Why this crop?</strong><br />{result.explanation}
        </div>
        {result.top_alternatives?.length > 0 && (
          <div className="alt-chips">
            <span style={{ fontSize: ".78rem", opacity: .7 }}>Also consider:</span>
            {result.top_alternatives.map(a => (
              <span key={a} className="alt-chip">{CROP_EMOJIS[a] || "🌱"} {a}</span>
            ))}
          </div>
        )}
      </div>

      {/* ── Profit hero ────────────────────────────────────────────────── */}
      {profit && (
        <div className="profit-hero">
          <div style={{ fontSize: ".85rem", opacity: .8, marginBottom: 4 }}>
            Expected Profit {profit.hectares > 1 ? `(${profit.hectares} hectares)` : "(per hectare)"}
          </div>
          <div className="profit-amount" style={{ color: profit.is_profitable ? "#fbbf24" : "#fca5a5" }}>
            {profit.profit_label}
          </div>
          <div className="profit-label">
            ROI: {profit.roi_percent}% &nbsp;|&nbsp; Break-even: {profit.breakeven_yield_t}t
          </div>

          <button
            className="btn btn-ghost btn-sm"
            style={{ marginTop: 14, color: "rgba(255,255,255,.8)", borderColor: "rgba(255,255,255,.3)" }}
            onClick={() => setShowCosts(s => !s)}
          >
            {showCosts ? "Hide" : "Show"} Cost Breakdown
          </button>

          {showCosts && (
            <div style={{ marginTop: 14, background: "rgba(255,255,255,.1)", borderRadius: 10, padding: "14px 18px" }}>
              {[
                ["Market Price",  `Rs.${profit.market_price_inr?.toLocaleString("en-IN")}/tonne`, ""],
                ["Total Revenue", profit.revenue_label, "green"],
                ["Fertilizer",    `Rs.${profit.cost_breakdown?.fertilizer_inr?.toLocaleString("en-IN")}`, ""],
                ["Water/Irrigation", `Rs.${profit.cost_breakdown?.water_inr?.toLocaleString("en-IN")}`, ""],
                ["Labor",         `Rs.${profit.cost_breakdown?.labor_inr?.toLocaleString("en-IN")}`, ""],
                ["Seeds",         `Rs.${profit.cost_breakdown?.seeds_inr?.toLocaleString("en-IN")}`, ""],
                ["Misc",          `Rs.${profit.cost_breakdown?.misc_inr?.toLocaleString("en-IN")}`, ""],
                ["Total Cost",    profit.cost_label, "red"],
                ["Net Profit",    profit.profit_label, profit.is_profitable ? "green" : "red"],
              ].map(([label, value, cls]) => (
                <div key={label} style={{
                  display: "flex", justifyContent: "space-between",
                  padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,.1)",
                  fontSize: ".88rem",
                }}>
                  <span style={{ opacity: .8 }}>{label}</span>
                  <span style={{
                    fontWeight: 700,
                    color: cls === "green" ? "#86efac" : cls === "red" ? "#fca5a5" : "white"
                  }}>{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Model accuracy note ─────────────────────────────────────────── */}
      {result.model_accuracy && (
        <div style={{ fontSize: ".78rem", color: "var(--gray-500)", textAlign: "center" }}>
          Model accuracy: {(result.model_accuracy * 100).toFixed(1)}%
        </div>
      )}
    </div>
  );
}
