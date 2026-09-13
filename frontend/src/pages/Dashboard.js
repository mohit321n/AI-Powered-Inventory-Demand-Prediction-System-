import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, Card, CardContent, Chip, Select, MenuItem, FormControl, InputLabel, useTheme } from '@mui/material';
import { TrendingUp, Inventory, Warning, AttachMoney, ArrowUpward, ArrowDownward } from '@mui/icons-material';
import api from '../services/api';
import SalesTrendChart from '../charts/SalesTrendChart';
import CategorySalesChart from '../charts/CategorySalesChart';
import TopProductsChart from '../charts/TopProductsChart';
import InventoryLevelChart from '../charts/InventoryLevelChart';

export default function Dashboard() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const [stats, setStats] = useState(null);
  const [salesTrend, setSalesTrend] = useState([]);
  const [categorySales, setCategorySales] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [inventoryLevels, setInventoryLevels] = useState([]);
  const [timeRange, setTimeRange] = useState(30);
  const [loading, setLoading] = useState(true);

  const mutedColor = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)';

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, salesRes, catRes, topRes, invRes] = await Promise.all([
        api.get('/dashboard/stats').catch(() => ({ data: { total_products: 0, total_inventory_value: 0, low_stock_count: 0, pending_alerts: 0, total_sales_today: 0, sales_change: 0 } })),
        api.get(`/dashboard/sales-trends?days=${timeRange}`).catch(() => ({ data: generateMockSalesTrend() })),
        api.get('/dashboard/category-sales').catch(() => ({ data: generateMockCategorySales() })),
        api.get('/dashboard/top-products').catch(() => ({ data: generateMockTopProducts() })),
        api.get('/dashboard/inventory-trends').catch(() => ({ data: generateMockInventoryLevels() })),
      ]);
      setStats(statsRes.data);
      setSalesTrend(salesRes.data);
      setCategorySales(catRes.data);
      setTopProducts(topRes.data);
      setInventoryLevels(invRes.data);
    } catch (err) {
      setStats({ total_products: 0, total_inventory_value: 0, low_stock_count: 0, pending_alerts: 0, total_sales_today: 0, sales_change: 0 });
      setSalesTrend(generateMockSalesTrend());
      setCategorySales(generateMockCategorySales());
      setTopProducts(generateMockTopProducts());
      setInventoryLevels(generateMockInventoryLevels());
    }
    setLoading(false);
  };

  function generateMockSalesTrend() {
    const data = [];
    for (let i = timeRange; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      data.push({ date: d.toISOString().split('T')[0], sales: Math.floor(Math.random() * 5000) + 2000, revenue: Math.floor(Math.random() * 15000) + 5000 });
    }
    return data;
  }

  function generateMockCategorySales() {
    return [
      { category: 'Electronics', sales: 45000 },
      { category: 'Clothing', sales: 32000 },
      { category: 'Home & Garden', sales: 28000 },
      { category: 'Sports', sales: 18000 },
      { category: 'Books', sales: 12000 },
      { category: 'Food', sales: 38000 },
    ];
  }

  function generateMockTopProducts() {
    return [
      { name: 'Wireless Earbuds', sales: 1240, revenue: 24800 },
      { name: 'Smart Watch', sales: 980, revenue: 19600 },
      { name: 'Laptop Stand', sales: 856, revenue: 12840 },
      { name: 'USB-C Hub', sales: 742, revenue: 8904 },
      { name: 'Mechanical Keyboard', sales: 621, revenue: 18630 },
      { name: 'Monitor Light Bar', sales: 534, revenue: 10680 },
    ];
  }

  function generateMockInventoryLevels() {
    return [
      { product: 'Wireless Earbuds', stock: 245, reorder: 50 },
      { product: 'Smart Watch', stock: 178, reorder: 40 },
      { product: 'Laptop Stand', stock: 342, reorder: 30 },
      { product: 'USB-C Hub', stock: 89, reorder: 60 },
      { product: 'Mechanical Keyboard', stock: 156, reorder: 45 },
      { product: 'Monitor Light Bar', stock: 28, reorder: 50 },
    ];
  }

  const statCards = [
    { title: 'Total Products', value: stats?.total_products || 0, icon: <Inventory />, color: '#6c63ff', change: '+12%', up: true },
    { title: 'Inventory Value', value: `₹${(stats?.total_inventory_value || 0).toLocaleString()}`, icon: <AttachMoney />, color: '#00c853', change: '+8%', up: true },
    { title: 'Low Stock Items', value: stats?.low_stock_count || 0, icon: <Warning />, color: '#ff9800', change: '-3', up: false },
    { title: 'Pending Alerts', value: stats?.pending_alerts || 0, icon: <TrendingUp />, color: '#ff6584', change: '+2', up: true },
  ];

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Dashboard</Typography>
          <Typography variant="body2" color={mutedColor}>Overview of your inventory and sales performance</Typography>
        </Box>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Time Range</InputLabel>
          <Select value={timeRange} label="Time Range" onChange={(e) => setTimeRange(e.target.value)}>
            <MenuItem value={7}>Last 7 days</MenuItem>
            <MenuItem value={30}>Last 30 days</MenuItem>
            <MenuItem value={90}>Last 90 days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {statCards.map((card, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card className="stat-card" sx={{ animation: `fadeIn 0.4s ease-out ${i * 0.1}s both` }}>
              <CardContent sx={{ p: '0 !important' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box className="icon-wrapper" sx={{ bgcolor: `${card.color}20` }}>
                    <Box sx={{ color: card.color, display: 'flex' }}>{card.icon}</Box>
                  </Box>
                  <Chip
                    size="small"
                    icon={card.up ? <ArrowUpward sx={{ fontSize: 14 }} /> : <ArrowDownward sx={{ fontSize: 14 }} />}
                    label={card.change}
                    sx={{ bgcolor: card.up ? 'rgba(0,200,83,0.12)' : 'rgba(255,23,68,0.12)', color: card.up ? '#00c853' : '#ff1744', fontWeight: 600, fontSize: 11 }}
                  />
                </Box>
                <Typography variant="h4" fontWeight={700}>{card.value}</Typography>
                <Typography variant="body2" color={mutedColor} sx={{ mt: 0.5 }}>{card.title}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card className="chart-card">
            <Typography variant="h6" sx={{ mb: 2 }}>Sales Trend</Typography>
            <SalesTrendChart data={salesTrend} />
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card className="chart-card">
            <Typography variant="h6" sx={{ mb: 2 }}>Sales by Category</Typography>
            <CategorySalesChart data={categorySales} />
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card className="chart-card">
            <Typography variant="h6" sx={{ mb: 2 }}>Top Products</Typography>
            <TopProductsChart data={topProducts} />
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card className="chart-card">
            <Typography variant="h6" sx={{ mb: 2 }}>Inventory Levels</Typography>
            <InventoryLevelChart data={inventoryLevels} />
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
