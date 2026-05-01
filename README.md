# 🌾 Smart Agriculture AI System

An AI-powered full-stack web application that helps farmers make data-driven decisions using weather data, soil conditions, and machine learning predictions.

---

## 📁 Project Structure

```
smart-agriculture-ai/
├── backend/                  # Python Flask API
│   ├── app.py                # Main Flask application
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
├── model/                    # ML model pipeline
│   ├── train.py              # Model training script
│   ├── predict.py            # Inference pipeline
│   ├── generate_data.py      # Synthetic dataset generator
│   └── crop_model.pkl        # Trained model (generated after training)
├── frontend/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

---

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Train the model first:
```bash
cd ../model
python generate_data.py   # generates synthetic dataset
python train.py           # trains and saves the model
```

Start the Flask server:
```bash
cd ../backend
python app.py
```
Backend runs at: `http://localhost:5000`

---

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:5173`

---

## 🔌 API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| POST   | /predict   | Get crop recommendation + yield    |
| POST   | /train     | Retrain the ML model               |
| GET    | /data      | Get sample/historical data         |
| GET    | /health    | Health check                       |

### Example `/predict` Request
```json
{
  "nitrogen": 90,
  "phosphorus": 42,
  "potassium": 43,
  "temperature": 20.8,
  "humidity": 82.0,
  "ph": 6.5,
  "rainfall": 202.9,
  "soil_type": "loamy"
}
```

### Example `/predict` Response
```json
{
  "crop": "rice",
  "confidence": 0.94,
  "expected_yield": 4.2,
  "explanation": "High humidity (82%) and adequate rainfall (202.9mm) strongly favor rice cultivation. The soil pH of 6.5 is optimal.",
  "feature_importance": { "humidity": 0.28, "rainfall": 0.24, ... },
  "top_alternatives": ["maize", "wheat"]
}
```

---

## ☁️ Deployment

### Frontend → Netlify
1. Build the frontend: `cd frontend && npm run build`
2. Drag the `dist/` folder to [netlify.com/drop](https://netlify.com/drop)
3. Or connect your GitHub repo and set build command: `npm run build`, publish dir: `dist`

### Backend → Render
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect repo, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. Add environment variable: `FLASK_ENV=production`
5. Copy the Render URL and update `VITE_API_URL` in frontend `.env`

### Backend → Railway (Alternative)
1. Install Railway CLI: `npm install -g @railway/cli`
2. `railway login && railway init && railway up`

---

## 🌱 How This Helps Real Farmers

- **Reduces guesswork**: Instead of relying on tradition alone, farmers get data-backed crop suggestions
- **Maximizes yield**: ML model trained on soil + climate data recommends the most productive crop
- **Saves resources**: Prevents planting wrong crops that waste water, fertilizer, and labor
- **Accessible**: Simple UI works on mobile browsers — no app install needed
- **Explainable AI**: Farmers understand *why* a crop is recommended, building trust

---

## 🔮 Future Improvements

- [ ] Integrate real weather APIs (OpenWeatherMap, Tomorrow.io)
- [ ] Add satellite imagery analysis (NDVI for crop health)
- [ ] IoT sensor integration for real-time soil data
- [ ] Mobile app (React Native)
- [ ] Offline mode with cached predictions
- [ ] Government scheme recommendations based on crop + region
- [ ] Pest and disease prediction module
- [ ] Market price forecasting for selected crops

---

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React 18, Vite, Chart.js, Axios   |
| Backend    | Python, Flask, Flask-CORS         |
| ML Model   | scikit-learn (Random Forest)      |
| Charts     | Chart.js via react-chartjs-2      |
| Styling    | CSS3 with CSS Variables           |

---

## 📄 License
MIT — free to use for educational and internship projects.
