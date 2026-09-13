import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Card, Button, TextField, Grid, Select, MenuItem, FormControl, InputLabel, Chip, InputAdornment } from '@mui/material';
import { Upload, Search, CalendarToday, TrendingUp } from '@mui/icons-material';
import api from '../services/api';
import useThemeColors from '../services/useThemeColors';

export default function Sales() {
  const c = useThemeColors();
  const [sales, setSales] = useState([]);
  const [search, setSearch] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [summary, setSummary] = useState({ totalSales: 0, totalRevenue: 0, avgOrder: 0, orderCount: 0 });
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchSales(); }, []);

  useEffect(() => {
    const filtered = getFilteredSales();
    const totalRev = filtered.reduce((sum, s) => sum + s.total, 0);
    setSummary({
      totalSales: filtered.reduce((sum, s) => sum + s.quantity, 0),
      totalRevenue: totalRev,
      avgOrder: filtered.length ? totalRev / filtered.length : 0,
      orderCount: filtered.length,
    });
  }, [sales, search, dateFrom, dateTo]);

  const fetchSales = async () => {
    try {
      const res = await api.get('/sales');
      setSales(res.data);
    } catch {
      setSales([
        { id: 1, product_name: 'Wireless Earbuds', quantity: 5, unit_price: 49.99, total: 249.95, date: '2026-09-12T10:30:00', channel: 'Online', customer: 'John D.' },
        { id: 2, product_name: 'Smart Watch', quantity: 2, unit_price: 199.99, total: 399.98, date: '2026-09-12T14:20:00', channel: 'Store', customer: 'Sarah M.' },
        { id: 3, product_name: 'Laptop Stand', quantity: 3, unit_price: 29.99, total: 89.97, date: '2026-09-11T09:15:00', channel: 'Online', customer: 'Mike R.' },
        { id: 4, product_name: 'USB-C Hub', quantity: 10, unit_price: 34.99, total: 349.90, date: '2026-09-11T16:45:00', channel: 'Wholesale', customer: 'TechCorp' },
        { id: 5, product_name: 'Mechanical Keyboard', quantity: 1, unit_price: 89.99, total: 89.99, date: '2026-09-10T11:30:00', channel: 'Online', customer: 'Alex K.' },
      ]);
    }
    setLoading(false);
  };

  const getFilteredSales = () => {
    return sales.filter(s => {
      const matchSearch = s.product_name.toLowerCase().includes(search.toLowerCase()) || s.customer.toLowerCase().includes(search.toLowerCase());
      const saleDate = new Date(s.date);
      const matchFrom = !dateFrom || saleDate >= new Date(dateFrom);
      const matchTo = !dateTo || saleDate <= new Date(dateTo + 'T23:59:59');
      return matchSearch && matchFrom && matchTo;
    });
  };

  const handleUploadCSV = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post('/sales/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      fetchSales();
    } catch {
      alert('CSV uploaded (simulated). Backend API not available.');
    }
    event.target.value = '';
  };

  const getChannelColor = (channel) => {
    const colors = { Online: '#6c63ff', Store: '#00c853', Wholesale: '#ff9800', 'Marketplace': '#ff6584' };
    return colors[channel] || '#999';
  };

  const filteredSales = getFilteredSales();

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Sales</Typography>
          <Typography variant="body2" color={c.subtitle}>Track sales performance and upload transaction data</Typography>
        </Box>
        <Button variant="contained" startIcon={<Upload />} onClick={() => fileInputRef.current.click()} sx={{ background: 'linear-gradient(135deg, #6c63ff, #5a52d5)', px: 3 }}>
          Upload CSV
        </Button>
        <input ref={fileInputRef} type="file" accept=".csv" hidden onChange={handleUploadCSV} />
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { title: 'Total Orders', value: summary.orderCount, color: '#6c63ff' },
          { title: 'Total Units Sold', value: summary.totalSales, color: '#00c853' },
          { title: 'Total Revenue', value: `$${summary.totalRevenue.toFixed(2)}`, color: '#ff9800' },
          { title: 'Avg Order Value', value: `$${summary.avgOrder.toFixed(2)}`, color: '#ff6584' },
        ].map((item, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card className="stat-card">
              <Typography variant="h5" fontWeight={700} sx={{ color: item.color }}>{item.value}</Typography>
              <Typography variant="caption" color={c.subtitle}>{item.title}</Typography>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card className="chart-card" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Search sales..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: c.inputBg } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><Search sx={{ color: c.muted }} /></InputAdornment> }}
          />
          <TextField size="small" type="date" label="From" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} InputLabelProps={{ shrink: true }} sx={{ minWidth: 150 }} />
          <TextField size="small" type="date" label="To" value={dateTo} onChange={(e) => setDateTo(e.target.value)} InputLabelProps={{ shrink: true }} sx={{ minWidth: 150 }} />
        </Box>
      </Card>

      <Card className="chart-card">
        <Box sx={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Product</th>
                <th>Customer</th>
                <th>Channel</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {filteredSales.map((s) => (
                <tr key={s.id}>
                  <td>{new Date(s.date).toLocaleDateString()}</td>
                  <td style={{ fontWeight: 500 }}>{s.product_name}</td>
                  <td>{s.customer}</td>
                  <td>
                    <Chip label={s.channel} size="small" sx={{ bgcolor: `${getChannelColor(s.channel)}20`, color: getChannelColor(s.channel), fontWeight: 600, fontSize: 11 }} />
                  </td>
                  <td>{s.quantity}</td>
                  <td>${s.unit_price.toFixed(2)}</td>
                  <td style={{ color: '#00c853', fontWeight: 600 }}>${s.total.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </Card>
    </Box>
  );
}
