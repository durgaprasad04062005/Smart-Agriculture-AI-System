/**
 * Chatbot.jsx — KrishiBot with voice input + API chat + Hindi support
 */
import React, { useState, useRef, useEffect } from "react";
import { sendChat } from "../api";

const INITIAL_MSG = {
  role: "bot",
  text: "Namaste! I'm KrishiBot, your AI farming assistant.\n\nAsk me about crops, soil, fertilizers, profit, or weather. I support English and Hindi!\n\nTip: After getting a prediction, ask me 'Why was this crop recommended?' for personalized advice.",
};

export default function Chatbot({ lastResult }) {
  const [messages, setMessages] = useState([INITIAL_MSG]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [lang, setLang]         = useState("en");
  const [listening, setListening] = useState(false);
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput("");

    const userMsg = { role: "user", text: msg };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    // Build history for context (last 6 turns)
    const history = messages.slice(-6).map(m => ({ role: m.role, text: m.text }));

    try {
      const res = await sendChat(msg, lastResult || null, history);
      setMessages(prev => [...prev, { role: "bot", text: res.response }]);
    } catch {
      // Fallback rule-based response
      setMessages(prev => [...prev, {
        role: "bot",
        text: lang === "hi"
          ? "माफ़ करें, सर्वर से जुड़ने में समस्या है। कृपया बाद में पुनः प्रयास करें।"
          : "Sorry, I couldn't reach the server. Please make sure the backend is running.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  // Voice input using Web Speech API
  const toggleVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser. Try Chrome.");
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = lang === "hi" ? "hi-IN" : "en-IN";
    rec.interimResults = false;
    rec.onresult = e => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      setListening(false);
    };
    rec.onerror = () => setListening(false);
    rec.onend   = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  };

  return (
    <div>
      {/* Language toggle */}
      <div style={{ display:"flex", gap:8, marginBottom:12 }}>
        {[["en","🇬🇧 English"],["hi","🇮🇳 हिंदी"]].map(([code, label]) => (
          <button key={code}
            className={`btn btn-sm ${lang === code ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setLang(code)}>
            {label}
          </button>
        ))}
        {lastResult && (
          <span style={{ marginLeft:"auto", fontSize:".78rem", color:"var(--green-700)",
            background:"var(--green-50)", padding:"4px 10px", borderRadius:12,
            border:"1px solid var(--green-200)" }}>
            Context: {lastResult.crop}
          </span>
        )}
      </div>

      <div className="chat-window">
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              {m.role === "bot" && <span style={{ marginRight:6, fontSize:".9rem" }}>🤖</span>}
              {m.text}
            </div>
          ))}
          {loading && (
            <div className="chat-msg bot typing">
              <span className="spinner spinner-dark" style={{ width:14, height:14 }} /> Thinking...
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-footer">
          <button
            className={`voice-btn ${listening ? "recording" : ""}`}
            onClick={toggleVoice}
            title={listening ? "Stop recording" : "Voice input"}
          >
            {listening ? "🔴" : "🎤"}
          </button>
          <input
            className="form-input"
            style={{ margin:0 }}
            placeholder={lang === "hi" ? "अपना सवाल लिखें..." : "Ask about crops, soil, profit..."}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
          />
          <button className="btn btn-primary btn-sm" onClick={() => send()} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
