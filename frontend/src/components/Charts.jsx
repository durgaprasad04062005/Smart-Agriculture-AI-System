/**
 * Charts.jsx
 * Reusable chart components using Chart.js + react-chartjs-2.
 * Includes: BarChart, PieChart, RadarChart, LineChart
 */
import React from "react";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  ArcElement, RadialLinearScale, PointElement,
  LineElement, Tooltip, Legend, Filler,
} from "chart.js";
import { Bar, Pie, Radar, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  ArcElement, RadialLinearScale, PointElement,
  LineElement, Tooltip, Legend, Filler
);

const GREEN_PALETTE = [
  "#1a5c2a", "#2d8a47", "#4caf50", "#66bb6a", "#81c784",
  "#a5d6a7", "#c8e6c9", "#388e3c", "#43a047", "#00897b",
  "#26a69a", "#00acc1", "#039be5", "#1e88e5", "#3949ab",
  "#5e35b1", "#8e24aa", "#d81b60", "#e53935", "#f4511e",
  "#fb8c00", "#fdd835", "#c0ca33", "#7cb342",
];

/* ── Bar Chart ──────────────────────────────────────────────────────────────── */
export function BarChart({ labels, values, title, color = "#2d8a47", horizontal = false }) {
  const data = {
    labels,
    datasets: [{
      label: title || "Value",
      data: values,
      backgroundColor: labels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length] + "cc"),
      borderColor:     labels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length]),
      borderWidth: 1.5,
      borderRadius: 6,
    }],
  };

  const options = {
    indexAxis: horizontal ? "y" : "x",
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (ctx) => ` ${ctx.parsed[horizontal ? "x" : "y"]}` } },
    },
    scales: {
      x: { grid: { color: "#f0f0f0" } },
      y: { grid: { color: "#f0f0f0" } },
    },
  };

  return <Bar data={data} options={options} />;
}

/* ── Pie Chart ──────────────────────────────────────────────────────────────── */
export function PieChart({ labels, values, title }) {
  const data = {
    labels,
    datasets: [{
      data: values,
      backgroundColor: labels.map((_, i) => GREEN_PALETTE[i % GREEN_PALETTE.length] + "dd"),
      borderColor: "white",
      borderWidth: 2,
    }],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "right", labels: { font: { size: 11 }, padding: 12 } },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
            const pct   = ((ctx.parsed / total) * 100).toFixed(1);
            return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
          },
        },
      },
    },
  };

  return <Pie data={data} options={options} />;
}

/* ── Radar Chart ────────────────────────────────────────────────────────────── */
export function RadarChart({ labels, values, label = "Input" }) {
  const data = {
    labels,
    datasets: [{
      label,
      data: values,
      backgroundColor: "rgba(45,138,71,0.15)",
      borderColor: "#2d8a47",
      borderWidth: 2,
      pointBackgroundColor: "#2d8a47",
      pointRadius: 4,
    }],
  };

  const options = {
    responsive: true,
    scales: {
      r: {
        beginAtZero: true,
        grid: { color: "#e0e0e0" },
        ticks: { font: { size: 10 } },
      },
    },
    plugins: { legend: { display: false } },
  };

  return <Radar data={data} options={options} />;
}

/* ── Line Chart ─────────────────────────────────────────────────────────────── */
export function LineChart({ labels, datasets, title }) {
  const data = {
    labels,
    datasets: datasets.map((ds, i) => ({
      label: ds.label,
      data:  ds.data,
      borderColor: GREEN_PALETTE[i * 3 % GREEN_PALETTE.length],
      backgroundColor: GREEN_PALETTE[i * 3 % GREEN_PALETTE.length] + "22",
      borderWidth: 2,
      pointRadius: 3,
      fill: true,
      tension: 0.4,
    })),
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
    },
    scales: {
      x: { grid: { color: "#f0f0f0" } },
      y: { grid: { color: "#f0f0f0" } },
    },
  };

  return <Line data={data} options={options} />;
}
