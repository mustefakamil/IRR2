import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, Filler,
} from "chart.js";
import { Line, Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, Title, Tooltip, Legend, Filler);

const GREEN = "#2e7d32";
const SKY = "#0288d1";
const AMBER = "#f9a825";
const RED = "#c62828";

const baseOpts = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false as const,
  interaction: { mode: "index" as const, intersect: false },
  plugins: { legend: { labels: { boxWidth: 12, font: { size: 11 } } } },
  scales: { x: { ticks: { maxTicksLimit: 12, font: { size: 10 } } }, y: { beginAtZero: true } },
};

export function EtEtcChart({ trends }: { trends: any[] }) {
  const labels = trends.map((d) => d.day);
  return (
    <div className="chart-wrap">
      <Line
        data={{
          labels,
          datasets: [
            { label: "ETo", data: trends.map((d) => d.eto), borderColor: SKY, backgroundColor: "transparent", tension: .3, pointRadius: 0, borderWidth: 2 },
            { label: "ETc", data: trends.map((d) => d.etc), borderColor: GREEN, backgroundColor: "transparent", tension: .3, pointRadius: 0, borderWidth: 2 },
          ],
        }}
        options={baseOpts}
      />
    </div>
  );
}

export function KcChart({ curve }: { curve: { day: number; kc: number }[] }) {
  return (
    <div className="chart-wrap">
      <Line
        data={{
          labels: curve.map((d) => d.day),
          datasets: [{ label: "Kc", data: curve.map((d) => d.kc), borderColor: GREEN,
            backgroundColor: "rgba(46,125,50,.12)", fill: true, tension: .25, pointRadius: 0, borderWidth: 2 }],
        }}
        options={baseOpts}
      />
    </div>
  );
}

export function SwbChart({ trends }: { trends: any[] }) {
  return (
    <div className="chart-wrap">
      <Line
        data={{
          labels: trends.map((d) => d.day),
          datasets: [
            { label: "Depletion", data: trends.map((d) => d.ds_end), borderColor: RED, backgroundColor: "rgba(198,40,40,.08)", fill: true, tension: .2, pointRadius: 0, borderWidth: 2 },
            { label: "RAW", data: trends.map((d) => d.raw), borderColor: AMBER, borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5 },
            { label: "TAW", data: trends.map((d) => d.taw), borderColor: "#8d6e63", borderDash: [3, 3], pointRadius: 0, borderWidth: 1.5 },
          ],
        }}
        options={baseOpts}
      />
    </div>
  );
}

export function WaterChart({ trends }: { trends: any[] }) {
  return (
    <div className="chart-wrap">
      <Bar
        data={{
          labels: trends.map((d) => d.day),
          datasets: [
            { label: "Irrigation Dg", data: trends.map((d) => d.dg), backgroundColor: GREEN },
            { label: "Effective Rain", data: trends.map((d) => d.pe), backgroundColor: SKY },
          ],
        }}
        options={{ ...baseOpts, scales: { ...baseOpts.scales, x: { ...baseOpts.scales.x, stacked: true }, y: { stacked: true, beginAtZero: true } } }}
      />
    </div>
  );
}
