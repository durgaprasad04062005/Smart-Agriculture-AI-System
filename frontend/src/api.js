/**
 * api.js — Axios wrapper for Smart Agriculture AI (Advanced)
 */
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "/api";

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: { "Content-Type": "application/json" },
});

export const predictCrop     = (data)          => client.post("/predict", data).then(r => r.data);
export const calculateProfit = (data)          => client.post("/profit",  data).then(r => r.data);
export const fetchWeather    = (city)          => client.post("/weather", { city }).then(r => r.data);
export const sendChat        = (message, context, history) =>
  client.post("/chat", { message, context, history }).then(r => r.data);
export const trainModel      = ()              => client.post("/train").then(r => r.data);
export const getSampleData   = ()              => client.get("/data?type=sample").then(r => r.data);
export const getHistory      = ()              => client.get("/data?type=history").then(r => r.data);
export const getModelMeta    = ()              => client.get("/meta").then(r => r.data);
export const getCrops        = ()              => client.get("/crops").then(r => r.data);
export const getMarketPrices = ()              => client.get("/prices").then(r => r.data);
export const healthCheck     = ()              => client.get("/health").then(r => r.data);
