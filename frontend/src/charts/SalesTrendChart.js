import React from 'react';
import { Box } from '@mui/material';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function SalesTrendChart({ data = [] }) {
  const chartData = {
    labels: data.map(d => {
      const date = new Date(d.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Revenue ($)',
        data: data.map(d => d.revenue || d.sales * 12),
        borderColor: '#6c63ff',
        backgroundColor: 'rgba(108, 99, 255, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#6c63ff',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
      },
      {
        label: 'Units Sold',
        data: data.map(d => d.sales),
        borderColor: '#ff6584',
        backgroundColor: 'rgba(255, 101, 132, 0.05)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#ff6584',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        borderDash: [5, 5],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: { color: 'rgba(255,255,255,0.6)', usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 12 } },
      },
      tooltip: {
        backgroundColor: '#1a1a2e',
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.8)',
        borderColor: 'rgba(108,99,255,0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        titleFont: { weight: 600 },
        callbacks: {
          label: (ctx) => {
            if (ctx.datasetIndex === 0) return `Revenue: $${ctx.parsed.y.toLocaleString()}`;
            return `Units: ${ctx.parsed.y.toLocaleString()}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 11 }, maxTicksLimit: 10 },
      },
      y: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: {
          color: 'rgba(255,255,255,0.4)',
          font: { size: 11 },
          callback: (v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v,
        },
      },
    },
  };

  return (
    <Box sx={{ height: 300, position: 'relative' }}>
      <Line data={chartData} options={options} />
    </Box>
  );
}
