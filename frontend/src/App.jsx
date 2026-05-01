/**
 * App.jsx — Smart Agriculture AI System (Advanced)
 * Tabs: Predict | Dashboard | History | Assistant | About
 */
import React, { useState } from "react";
import InputForm         from "./components/InputForm";
import ResultCard        from "./components/ResultCard";
import FeatureImportance from "./components/FeatureImportance";
import Dashboard         from "./components/Dashboard";
import History           from "./components/History";
import Chatbot           from "./components/Chatbot";
import { RadarChart }    from "./components/Charts";
import { predictCrop, trainModel } from "./api";

const TABS = [
  { id: "predict",   label: "🌾 Predict"    },
  { id: "dashboard", label: "📊 Dashboard"  },
  { id: "history",   label: "📋 History"    },
  { id: "chatbot",   label: "🤖 Assistant"  },
  { id: "about",     label: "ℹ️ About"      },
];

export default function App() {
  const [tab, setTab]           = useState("predict");
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [training, setTraining] = useState(false);
  const [trainMsg, setTrainMsg] = useState(null);

  const handlePredict = async (formData) => {
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await predictCrop(formData);
      setResult(res);
    } catch (e) {
      setError(e.response?.data?.error || e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true); setTrainMsg(null);
    try {
      const res = await trainModel();
      setTrainMsg(`Model retrained! Accuracy: ${(res.metadata?.accuracy * 100).toFixed(1)}%`);
    } catch (e) {
      setTrainMsg(`Training failed: ${e.response?.data?.error || e.message}`);
    } finally {
      setTraining(false);
    }
  };

  const radarData = result ? {
    labels: ["Nitrogen","Phosphorus","Potassium","Temperature","Humidity","pH","Rainfall"],
    values: [
      Math.min(result.input_features.N   / 2,   100),
      Math.min(result.input_features.P   / 2,   100),
      Math.min(result.input_features.K   / 2.5, 100),
      (result.input_features.temperature / 50)  * 100,
      result.input_features.humidity,
      (result.input_features.ph          / 14)  * 100,
      Math.min(result.input_features.rainfall / 5, 100),
    ],
  } : null;

  return (
    <div className="app-wrapper">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-logo">
            <div className="logo-icon">🌾</div>
            <span>Smart Agriculture AI</span>
            <span className="header-badge">Advanced</span>
          </div>
          <nav className="header-nav">
            {TABS.map(t => (
              <button key={t.id} className={`nav-btn ${tab === t.id ? "active" : ""}`}
                onClick={() => setTab(t.id)}>{t.label}</button>
            ))}
          </nav>
        </div>
      </header>

      {/* ── Main ────────────────────────────────────────────────────────── */}
      <main className="main-content">

        {/* Mobile tab bar */}
        <div className="tab-bar">
          {TABS.map(t => (
            <button key={t.id} className={`tab-btn ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}>
              {t.label.split(" ")[0]}
            </button>
          ))}
        </div>

        {/* ── PREDICT ─────────────────────────────────────────────────── */}
        {tab === "predict" && (
          <div>
            <div className="section-title">🌾 AI Crop Recommendation</div>
            <p className="section-subtitle">
              Enter your soil and climate data to get an AI-powered crop recommendation with profit forecast.
            </p>

            {/* Retrain strip */}
            <div style={{ display:"flex", gap:12, alignItems:"center", flexWrap:"wrap", marginBottom:20 }}>
              <button className="btn btn-ghost btn-sm" onClick={handleTrain} disabled={training}>
                {training ? <><span className="spinner spinner-dark" /> Retraining...</> : "⚙️ Retrain Model"}
              </button>
              {trainMsg && (
                <span className={`alert ${trainMsg.includes("failed") ? "alert-error" : "alert-success"}`}
                  style={{ margin:0, padding:"6px 14px" }}>
                  {trainMsg}
                </span>
              )}
            </div>

            <div className="grid-2" style={{ alignItems:"start" }}>
              {/* Left: Input */}
              <div className="card">
                <div className="card-title">📋 Farm Data Input</div>
                <InputForm onSubmit={handlePredict} loading={loading} />
              </div>

              {/* Right: Results */}
              <div style={{ display:"flex", flexDirection:"column", gap:20 }}>
                {error && (
                  <div className="alert alert-error">
                    ⚠️ {error}
                    {error.includes("Model not found") && (
                      <div style={{ marginTop:6 }}>Click <strong>Retrain Model</strong> above first.</div>
                    )}
                  </div>
                )}

                {!result && !error && !loading && (
                  <div className="card" style={{ textAlign:"center", padding:48 }}>
                    <div style={{ fontSize:"3.5rem", marginBottom:12 }}>🌱</div>
                    <div style={{ color:"var(--gray-500)", fontSize:".95rem" }}>
                      Enter your farm data and click<br />
                      <strong style={{ color:"var(--green-700)" }}>Get AI Recommendation</strong>
                    </div>
                  </div>
                )}

                {loading && (
                  <div className="card" style={{ textAlign:"center", padding:48 }}>
                    <div className="spinner spinner-dark" style={{ width:36, height:36, margin:"0 auto 16px" }} />
                    <div style={{ color:"var(--gray-500)" }}>Analyzing your farm data...</div>
                  </div>
                )}

                {result && (
                  <>
                    <ResultCard result={result} />

                    <div className="card">
                      <div className="card-title">📡 Input Feature Profile</div>
                      <RadarChart labels={radarData.labels} values={radarData.values} label="Your Farm" />
                    </div>

                    <div className="card">
                      <FeatureImportance importance={result.feature_importance} />
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ── DASHBOARD ───────────────────────────────────────────────── */}
        {tab === "dashboard" && (
          <div>
            <div className="section-title">📊 Analytics Dashboard</div>
            <p className="section-subtitle">Crop distribution, weather trends, and model performance metrics.</p>
            <Dashboard />
          </div>
        )}

        {/* ── HISTORY ─────────────────────────────────────────────────── */}
        {tab === "history" && (
          <div>
            <div className="section-title">📋 Prediction History</div>
            <p className="section-subtitle">All predictions made in this session with profit estimates.</p>
            <History />
          </div>
        )}

        {/* ── CHATBOT ─────────────────────────────────────────────────── */}
        {tab === "chatbot" && (
          <div>
            <div className="section-title">🤖 KrishiBot — Farmer Assistant</div>
            <p className="section-subtitle">Ask anything about crops, soil, fertilizers, or profit. Supports English & Hindi.</p>
            <div className="grid-2" style={{ alignItems:"start" }}>
              <div className="card">
                <div className="card-title">💬 Chat with KrishiBot</div>
                <Chatbot lastResult={result} />
              </div>
              <div className="card">
                <div className="card-title">💡 Try Asking</div>
                <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                  {[
                    "Why was this crop recommended?",
                    "How do I increase my yield?",
                    "Best fertilizer for rice?",
                    "What is the ideal soil pH?",
                    "How much profit can I expect?",
                    "Tell me about wheat farming",
                    "How to manage pests organically?",
                    "What government schemes are available?",
                    "How to save water in irrigation?",
                  ].map(q => (
                    <div key={q} style={{
                      padding:"9px 14px", background:"var(--green-50)",
                      borderRadius:8, fontSize:".88rem", color:"var(--green-900)",
                      border:"1px solid var(--green-200)", cursor:"default",
                    }}>
                      💬 {q}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── ABOUT ───────────────────────────────────────────────────── */}
        {tab === "about" && (
          <div style={{ display:"flex", flexDirection:"column", gap:24 }}>
            <div className="section-title">ℹ️ About Smart Agriculture AI</div>

            <div className="card">
              <div className="card-title">🎯 What is this system?</div>
              <p style={{ color:"var(--gray-500)", lineHeight:1.8 }}>
                Smart Agriculture AI is a production-ready full-stack application that helps Indian farmers
                make data-driven decisions. It combines machine learning (Random Forest), real-time weather
                data, and business analytics to recommend the best crop and predict profit — all in one place.
              </p>
            </div>

            <div className="grid-2">
              <div className="card">
                <div className="card-title">🌱 How It Helps Farmers</div>
                <ul style={{ color:"var(--gray-500)", lineHeight:2.2, paddingLeft:20 }}>
                  <li>AI-powered crop recommendation (87%+ accuracy)</li>
                  <li>Real-time weather auto-fill by city</li>
                  <li>Profit forecast with full cost breakdown</li>
                  <li>KrishiBot assistant in English + Hindi</li>
                  <li>Works on mobile — no app install needed</li>
                  <li>Explains <em>why</em> each crop is recommended</li>
                </ul>
              </div>
              <div className="card">
                <div className="card-title">🛠️ Tech Stack</div>
                <ul style={{ color:"var(--gray-500)", lineHeight:2.2, paddingLeft:20 }}>
                  <li><strong>Frontend:</strong> React 18 + Vite + Chart.js</li>
                  <li><strong>Backend:</strong> Python + Flask + REST API</li>
                  <li><strong>ML Model:</strong> scikit-learn Random Forest</li>
                  <li><strong>Weather:</strong> OpenWeatherMap API</li>
                  <li><strong>AI Chat:</strong> OpenAI GPT / Rule-based</li>
                  <li><strong>Deploy:</strong> Netlify + Render</li>
                </ul>
              </div>
            </div>

            <div className="card">
              <div className="card-title">💰 How Profit is Calculated</div>
              <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                {[
                  ["Expected Yield", "ML regression model predicts tonnes/hectare based on soil + climate"],
                  ["Total Revenue",  "Yield × Market Price (sourced from India MSP / mandi rates 2024)"],
                  ["Total Cost",     "Fertilizer + Water + Labor + Seeds + Misc (per hectare averages)"],
                  ["Net Profit",     "Revenue − Cost, shown in INR with Indian number formatting"],
                  ["ROI %",         "(Profit ÷ Cost) × 100 — tells you return on investment"],
                ].map(([term, desc]) => (
                  <div key={term} style={{ display:"flex", gap:12, padding:"10px 0", borderBottom:"1px solid var(--gray-100)" }}>
                    <div style={{ width:140, fontWeight:700, color:"var(--green-700)", fontSize:".88rem", flexShrink:0 }}>{term}</div>
                    <div style={{ color:"var(--gray-500)", fontSize:".88rem" }}>{desc}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-title">🔮 Future Improvements</div>
              <div className="grid-2">
                {[
                  ["🛰️","Satellite imagery (NDVI crop health)"],
                  ["📱","Mobile app (React Native)"],
                  ["🔌","IoT soil sensor integration"],
                  ["💹","Live market price API"],
                  ["🐛","Pest & disease prediction"],
                  ["🏛️","Government scheme matcher"],
                  ["📴","Offline PWA mode"],
                  ["🗺️","Regional language support (10+ languages)"],
                ].map(([icon, text]) => (
                  <div key={text} style={{ display:"flex", gap:10, padding:"8px 0", borderBottom:"1px solid var(--gray-100)", fontSize:".88rem" }}>
                    <span>{icon}</span>
                    <span style={{ color:"var(--gray-500)" }}>{text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="app-footer">
        🌾 Smart Agriculture AI System — Built for farmers, powered by machine learning.
        &nbsp;|&nbsp; <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>
      </footer>
    </div>
  );
}
