import React from 'react';
import { Box } from '@mui/material';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function DemandForecastChart({ data }) {
  if (!data) return null;

  const { historical = [], predicted = [], upper = [], lower = [] } = data;
  const allDates = [...historical, ...predicted].map(d => d.date);
  const labels = allDates.map(d => {
    const date = new Date(d);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  });

  const historicalData = allDates.map(d => {
    const found = historical.find(h => h.date === d);
    return found ? found.demand : null;
  });

  const predictedData = allDates.map(d => {
    const found = predicted.find(p => p.date === d);
    return found ? found.demand : null;
  });

  const upperData = allDates.map(d => {
    const found = upper.find(u => u.date === d);
    return found ? found.demand : null;
  });

  const lowerData = allDates.map(d => {
    const found = lower.find(l => l.date === d);
    return found ? found.demand : null;
  });

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Historical Demand',
        data: historicalData,
        borderColor: '#6c63ff',
        backgroundColor: 'rgba(108, 99, 255, 0.1)',
        borderWidth: 2.5,
        fill: false,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#6c63ff',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        spanGaps: false,
      },
      {
        label: 'Forecasted Demand',
        data: predictedData,
        borderColor: '#ff6584',
        backgroundColor: 'rgba(255, 101, 132, 0.1)',
        borderWidth: 2.5,
        borderDash: [6, 4],
        fill: false,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#ff6584',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        spanGaps: false,
      },
      {
        label: 'Upper Bound',
        data: upperData,
        borderColor: 'rgba(255, 101, 132, 0.2)',
        backgroundColor: 'rgba(255, 101, 132, 0.08)',
        borderWidth: 1,
        fill: '+1',
        tension: 0.4,
        pointRadius: 0,
        spanGaps: false,
      },
      {
        label: 'Lower Bound',
        data: lowerData,
        borderColor: 'rgba(255, 101, 132, 0.2)',
        backgroundColor: 'rgba(255, 101, 132, 0.08)',
        borderWidth: 1,
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        spanGaps: false,
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
        labels: {
          color: 'rgba(255,255,255,0.6)',
          usePointStyle: true,
          pointStyle: 'line',
          padding: 16,
          font: { size: 11 },
          filter: (item) => !item.text.includes('Bound'),
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
        filter: (item) => !item.dataset.label.includes('Bound'),
        callbacks: {
          label: (ctx) => {
            if (ctx.datasetIndex === 0) return `Historical: ${ctx.parsed.y} units`;
            return `Forecast: ${ctx.parsed.y} units`;
          },
        },
      },
      annotation: {
        annotations: {
          verticalLine: {
            type: 'line',
            xMin: historical.length - 1,
            xMax: historical.length - 1,
            borderColor: 'rgba(255,255,255,0.2)',
            borderWidth: 1,
            borderDash: [4, 4],
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 10 }, maxTicksLimit: 12 },
      },
      y: {
        grid: { color: 'rgba(108,99,255,0.05)', drawBorder: false },
        ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 11 } },
        beginAtZero: true,
      },
    },
  };

  return (
    <Box sx={{ height: 350, position: 'relative' }}>
      <Line data={chartData} options={options} />
    </Box>
  );
}
