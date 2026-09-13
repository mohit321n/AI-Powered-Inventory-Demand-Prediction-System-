import React from 'react';
import { Box } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function InventoryLevelChart({ data = [] }) {
  const chartData = {
    labels: data.map(d => d.product.length > 12 ? d.product.slice(0, 12) + '...' : d.product),
    datasets: [
      {
        label: 'Current Stock',
        data: data.map(d => d.stock),
        backgroundColor: data.map(d =>
          d.stock <= d.reorder ? 'rgba(255, 23, 68, 0.7)' :
          d.stock <= d.reorder * 1.5 ? 'rgba(255, 152, 0, 0.7)' :
          'rgba(108, 99, 255, 0.7)'
        ),
        borderColor: data.map(d =>
          d.stock <= d.reorder ? '#ff1744' :
          d.stock <= d.reorder * 1.5 ? '#ff9800' :
          '#6c63ff'
        ),
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false,
      },
      {
        label: 'Reorder Point',
        data: data.map(d => d.reorder),
        backgroundColor: 'rgba(255, 255, 255, 0.08)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        borderDash: [4, 4],
        borderRadius: 4,
        borderSkipped: false,
        barPercentage: 0.4,
        categoryPercentage: 0.8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: { color: 'rgba(255,255,255,0.6)', usePointStyle: true, pointStyle: 'rect', padding: 16, font: { size: 11 } },
      },
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
            if (ctx.datasetIndex === 0) {
              const item = data[ctx.dataIndex];
              const status = item.stock <= item.reorder ? ' (LOW!)' : '';
              return `Stock: ${item.stock}${status}`;
            }
            return `Reorder: ${data[ctx.dataIndex].reorder}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 10 }, maxRotation: 45 },
      },
      y: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 11 } },
        beginAtZero: true,
      },
    },
  };

  return (
    <Box sx={{ height: 300, position: 'relative' }}>
      <Bar data={chartData} options={options} />
    </Box>
  );
}
