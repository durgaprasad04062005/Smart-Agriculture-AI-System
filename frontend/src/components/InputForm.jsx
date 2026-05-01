/**
 * InputForm.jsx — Advanced version with real weather API fetch
 */
import React, { useState } from "react";
import { fetchWeather } from "../api";

const SOIL_TYPES = ["loamy", "clay", "sandy", "silty", "peaty", "chalky"];

const DEFAULTS = {
  nitrogen: 90, phosphorus: 42, potassium: 43,
  temperature: 25, humidity: 70, ph: 6.5, rainfall: 120,
  soil_type: "loamy", hectares: 1,
};

const FIELDS = [
  { key: "nitrogen",    label: "Nitrogen (N)",   unit: "mg/kg", min: 0,   max: 200, step: 1,   tip: "Primary macronutrient for leaf growth" },
  { key: "phosphorus",  label: "Phosphorus (P)", unit: "mg/kg", min: 0,   max: 200, step: 1,   tip: "Supports root development & flowering" },
  { key: "potassium",   label: "Potassium (K)",  unit: "mg/kg", min: 0,   max: 250, step: 1,   tip: "Improves disease resistance & yield" },
  { key: "temperature", label: "Temperature",    unit: "°C",    min: 0,   max: 50,  step: 0.1, tip: "Average ambient temperature" },
  { key: "humidity",    label: "Humidity",       unit: "%",     min: 0,   max: 100, step: 0.1, tip: "Relative humidity in the air" },
  { key: "ph",          label: "Soil pH",        unit: "pH",    min: 3.5, max: 9.5, step: 0.1, tip: "Soil acidity/alkalinity (7 = neutral)" },
  { key: "rainfall",    label: "Rainfall",       unit: "mm",    min: 0,   max: 500, step: 1,   tip: "Seasonal rainfall estimate" },
];

export default function InputForm({ onSubmit, loading }) {
  const [form, setForm]         = useState(DEFAULTS);
  const [city, setCity]         = useState("");
  const [weatherLoading, setWL] = useState(false);
  const [weatherInfo, setWI]    = useState(null);
  const [weatherError, setWE]   = useState(null);

  const set = (key, val) => setForm(p => ({ ...p, [key]: val }));

  const handleFetchWeather = async () => {
    if (!city.trim()) return;
    setWL(true); setWE(null); setWI(null);
    try {
      const w = await fetchWeather(city.trim());
      setForm(p => ({
        ...p,
        temperature: w.temperature,
        humidity:    w.humidity,
        rainfall:    w.rainfall,
      }));
      setWI(w);
    } catch (e) {
      setWE(e.response?.data?.error || e.message);
    } finally {
      setWL(false);
    }
  };

  return (
    <form onSubmit={e => { e.preventDefault(); onSubmit(form); }}>

      {/* ── Real-time weather fetch ──────────────────────────────────────── */}
      <div className="weather-strip">
        <span style={{ fontSize: "1.2rem" }}>🌤️</span>
        <span style={{ fontSize: ".85rem", color: "var(--blue-600)", fontWeight: 600, flex: 1 }}>
          Auto-fill weather by city
        </span>
        <input
          className="form-input"
          style={{ width: 180, margin: 0 }}
          placeholder="e.g. Mumbai, Delhi..."
          value={city}
          onChange={e => setCity(e.target.value)}
          onKeyDown={e => e.key === "Enter" && (e.preventDefault(), handleFetchWeather())}
        />
        <button
          type="button"
          className="btn btn-amber btn-sm"
          onClick={handleFetchWeather}
          disabled={weatherLoading || !city.trim()}
        >
          {weatherLoading ? <span className="spinner" /> : "Fetch Weather"}
        </button>
      </div>

      {weatherError && <div className="alert alert-error" style={{ marginBottom: 12 }}>⚠️ {weatherError}</div>}

      {weatherInfo && (
        <div className="weather-card" style={{ marginBottom: 16, padding: "14px 18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="weather-city">📍 {weatherInfo.city}{weatherInfo.country ? `, ${weatherInfo.country}` : ""}</div>
              <div className="weather-temp">{weatherInfo.temperature}°C</div>
              <div style={{ fontSize: ".85rem", opacity: .85 }}>{weatherInfo.description}</div>
            </div>
            <div style={{ textAlign: "right", fontSize: ".85rem", opacity: .9 }}>
              <div>💧 {weatherInfo.humidity}% humidity</div>
              <div>🌧️ {weatherInfo.rainfall}mm rainfall</div>
              <div className="weather-badge">{weatherInfo.source === "openweathermap" ? "Live Data" : "Simulated"}</div>
            </div>
          </div>
        </div>
      )}

      {/* ── Soil type + farm size ────────────────────────────────────────── */}
      <div className="grid-2">
        <div className="form-group">
          <label className="form-label">🪨 Soil Type</label>
          <select className="form-select" value={form.soil_type} onChange={e => set("soil_type", e.target.value)}>
            {SOIL_TYPES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">📐 Farm Size</label>
          <div className="input-with-unit">
            <input
              type="number" className="form-input" style={{ paddingRight: 60 }}
              value={form.hectares} min={0.1} max={1000} step={0.1}
              onChange={e => set("hectares", parseFloat(e.target.value) || 1)}
            />
            <span className="input-unit">hectares</span>
          </div>
        </div>
      </div>

      {/* ── Numeric fields ───────────────────────────────────────────────── */}
      <div className="grid-2">
        {FIELDS.map(({ key, label, unit, min, max, step, tip }) => (
          <div className="form-group" key={key}>
            <label className="form-label" title={tip}>{label}</label>
            <div className="input-with-unit">
              <input
                type="number" className="form-input" style={{ paddingRight: 52 }}
                value={form[key]} min={min} max={max} step={step}
                onChange={e => set(key, parseFloat(e.target.value) || 0)}
                required
              />
              <span className="input-unit">{unit}</span>
            </div>
            <div style={{ fontSize: ".72rem", color: "var(--gray-500)", marginTop: 2 }}>{tip}</div>
          </div>
        ))}
      </div>

      <button type="submit" className="btn btn-primary btn-full" disabled={loading} style={{ marginTop: 4 }}>
        {loading ? <><span className="spinner" /> Analyzing your farm data...</> : "🌾 Get AI Recommendation"}
      </button>
    </form>
  );
}
