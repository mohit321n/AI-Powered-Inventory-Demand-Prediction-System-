import React from 'react';
import { Box, Typography } from '@mui/material';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function CategorySalesChart({ data = [] }) {
  const colors = ['#6c63ff', '#ff6584', '#00c853', '#ff9800', '#00b0ff', '#9c27b0', '#e91e63', '#00bcd4'];
  const borderColors = colors.map(c => c);

  const chartData = {
    labels: data.map(d => d.category),
    datasets: [
      {
        data: data.map(d => d.sales),
        backgroundColor: colors.slice(0, data.length),
        borderColor: borderColors.slice(0, data.length),
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  const total = data.reduce((sum, d) => sum + d.sales, 0);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: 'rgba(255,255,255,0.6)',
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 12,
          font: { size: 11 },
        },
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
            const value = ctx.parsed;
            const percentage = ((value / total) * 100).toFixed(1);
            return `$${value.toLocaleString()} (${percentage}%)`;
          },
        },
      },
    },
  };

  const centerText = {
    id: 'centerText',
    afterDraw(chart) {
      const { ctx, chartArea: { width, height, top } } = chart;
      ctx.save();
      ctx.font = 'bold 24px Inter, sans-serif';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`$${(total / 1000).toFixed(0)}k`, width / 2, top + height / 2 - 8);
      ctx.font = '12px Inter, sans-serif';
      ctx.fillStyle = 'rgba(255,255,255,0.5)';
      ctx.fillText('Total Sales', width / 2, top + height / 2 + 14);
      ctx.restore();
    },
  };

  return (
    <Box sx={{ height: 300, position: 'relative' }}>
      <Pie data={chartData} options={options} plugins={[centerText]} />
    </Box>
  );
}
