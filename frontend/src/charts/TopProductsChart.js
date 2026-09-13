import React from 'react';
import { Box } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function TopProductsChart({ data = [] }) {
  const colors = ['#6c63ff', '#ff6584', '#00c853', '#ff9800', '#00b0ff', '#9c27b0'];

  const chartData = {
    labels: data.map(d => d.name.length > 15 ? d.name.slice(0, 15) + '...' : d.name),
    datasets: [
      {
        label: 'Revenue ($)',
        data: data.map(d => d.revenue),
        backgroundColor: data.map((_, i) => `${colors[i % colors.length]}B3`),
        borderColor: data.map((_, i) => colors[i % colors.length]),
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1a1a2e',
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.8)',
        borderColor: 'rgba(108,99,255,0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: (ctx) => {
            const item = data[ctx.dataIndex];
            return [`Revenue: $${item.revenue.toLocaleString()}`, `Units Sold: ${item.sales.toLocaleString()}`];
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: {
          color: 'rgba(255,255,255,0.4)',
          font: { size: 11 },
          callback: (v) => v >= 1000 ? `$${(v / 1000).toFixed(0)}k` : `$${v}`,
        },
      },
      y: {
        grid: { display: false },
        ticks: { color: 'rgba(255,255,255,0.6)', font: { size: 11, weight: 500 } },
      },
    },
  };

  return (
    <Box sx={{ height: 300, position: 'relative' }}>
      <Bar data={chartData} options={options} />
    </Box>
  );
}
