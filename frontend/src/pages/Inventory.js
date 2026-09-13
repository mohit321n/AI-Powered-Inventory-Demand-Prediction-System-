import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, Button, TextField, Select, MenuItem, FormControl, InputLabel, Grid, Dialog, DialogTitle, DialogContent, DialogActions, Chip, InputAdornment } from '@mui/material';
import { Add, SwapHoriz, Search, TrendingUp, TrendingDown, Inventory as InventoryIcon } from '@mui/icons-material';
import api from '../services/api';
import useThemeColors from '../services/useThemeColors';

export default function Inventory() {
  const c = useThemeColors();
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [openModal, setOpenModal] = useState(false);
  const [formData, setFormData] = useState({ product_id: '', type: 'purchase', quantity: '', notes: '', unit_cost: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [transRes, prodRes] = await Promise.all([
        api.get('/inventory/transactions'),
        api.get('/products'),
      ]);
      setTransactions(transRes.data);
      setProducts(prodRes.data);
    } catch {
      setProducts([
        { id: 1, name: 'Wireless Earbuds', current_stock: 245, min_stock: 50, max_stock: 500 },
        { id: 2, name: 'Smart Watch', current_stock: 178, min_stock: 30, max_stock: 300 },
        { id: 3, name: 'Laptop Stand', current_stock: 342, min_stock: 40, max_stock: 400 },
        { id: 4, name: 'USB-C Hub', current_stock: 89, min_stock: 60, max_stock: 350 },
        { id: 5, name: 'Mechanical Keyboard', current_stock: 156, min_stock: 45, max_stock: 250 },
        { id: 6, name: 'Monitor Light Bar', current_stock: 28, min_stock: 50, max_stock: 200 },
      ]);
      setTransactions([
        { id: 1, product_name: 'Wireless Earbuds', type: 'purchase', quantity: 100, unit_cost: 12.50, date: '2026-09-12T10:30:00', notes: 'Restock from supplier' },
        { id: 2, product_name: 'Smart Watch', type: 'sale', quantity: 15, unit_cost: 45.00, date: '2026-09-12T14:20:00', notes: 'Online order #1234' },
        { id: 3, product_name: 'USB-C Hub', type: 'adjustment', quantity: -5, unit_cost: 10.00, date: '2026-09-11T09:15:00', notes: 'Damaged items' },
        { id: 4, product_name: 'Laptop Stand', type: 'purchase', quantity: 200, unit_cost: 8.00, date: '2026-09-10T16:45:00', notes: 'Bulk order' },
        { id: 5, product_name: 'Monitor Light Bar', type: 'sale', quantity: 8, unit_cost: 15.00, date: '2026-09-10T11:30:00', notes: 'Store sale' },
      ]);
    }
    setLoading(false);
  };

  const filtered = transactions.filter(t => {
    const matchSearch = t.product_name.toLowerCase().includes(search.toLowerCase()) || t.notes.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === 'all' || t.type === typeFilter;
    return matchSearch && matchType;
  });

  const handleSubmit = async () => {
    try {
      await api.post('/inventory/transactions', formData);
      fetchData();
      setOpenModal(false);
      setFormData({ product_id: '', type: 'purchase', quantity: '', notes: '', unit_cost: '' });
    } catch {
      const product = products.find(p => p.id === parseInt(formData.product_id));
      if (product) {
        const newTrans = { id: Date.now(), product_name: product.name, type: formData.type, quantity: parseInt(formData.quantity), unit_cost: parseFloat(formData.unit_cost) || 0, date: new Date().toISOString(), notes: formData.notes };
        setTransactions([newTrans, ...transactions]);
      }
      setOpenModal(false);
      setFormData({ product_id: '', type: 'purchase', quantity: '', notes: '', unit_cost: '' });
    }
  };

  const getTypeColor = (type) => {
    const colors = { purchase: '#00c853', sale: '#6c63ff', adjustment: '#ff9800', return: '#00b0ff', transfer: '#ff6584' };
    return colors[type] || '#999';
  };

  const totalIn = transactions.filter(t => ['purchase', 'return'].includes(t.type)).reduce((sum, t) => sum + Math.abs(t.quantity), 0);
  const totalOut = transactions.filter(t => ['sale', 'adjustment'].includes(t.type)).reduce((sum, t) => sum + Math.abs(t.quantity), 0);
  const lowStockCount = products.filter(p => p.current_stock <= p.min_stock).length;

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Inventory</Typography>
          <Typography variant="body2" color={c.subtitle}>Track stock levels and transactions</Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenModal(true)} sx={{ background: 'linear-gradient(135deg, #6c63ff, #5a52d5)', px: 3 }}>
          New Transaction
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { title: 'Total Products', value: products.length, icon: <InventoryIcon />, color: '#6c63ff' },
          { title: 'Stock In', value: totalIn, icon: <TrendingUp />, color: '#00c853' },
          { title: 'Stock Out', value: totalOut, icon: <TrendingDown />, color: '#ff6584' },
          { title: 'Low Stock Alerts', value: lowStockCount, icon: <InventoryIcon />, color: '#ff9800' },
        ].map((item, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card className="stat-card">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ width: 48, height: 48, borderRadius: 2, bgcolor: `${item.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: item.color }}>{item.icon}</Box>
                <Box>
                  <Typography variant="h5" fontWeight={700}>{item.value}</Typography>
                  <Typography variant="caption" color={c.subtitle}>{item.title}</Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card className="chart-card" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search transactions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: c.inputBg } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><Search sx={{ color: c.muted }} /></InputAdornment> }}
          />
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Type</InputLabel>
            <Select value={typeFilter} label="Type" onChange={(e) => setTypeFilter(e.target.value)}>
              <MenuItem value="all">All Types</MenuItem>
              {['purchase', 'sale', 'adjustment', 'return', 'transfer'].map(t => <MenuItem key={t} value={t} sx={{ textTransform: 'capitalize' }}>{t}</MenuItem>)}
            </Select>
          </FormControl>
        </Box>
      </Card>

      <Card className="chart-card">
        <Box sx={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Product</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Unit Cost</th>
                <th>Total Value</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id}>
                  <td>{new Date(t.date).toLocaleDateString()}</td>
                  <td style={{ fontWeight: 500 }}>{t.product_name}</td>
                  <td>
                    <Chip label={t.type} size="small" sx={{ bgcolor: `${getTypeColor(t.type)}20`, color: getTypeColor(t.type), textTransform: 'capitalize', fontWeight: 600, fontSize: 11 }} />
                  </td>
                  <td style={{ color: t.quantity > 0 ? '#00c853' : '#ff6584', fontWeight: 600 }}>
                    {t.quantity > 0 ? '+' : ''}{t.quantity}
                  </td>
                  <td>${t.unit_cost.toFixed(2)}</td>
                  <td>${Math.abs(t.quantity * t.unit_cost).toFixed(2)}</td>
                  <td color={c.subtitle}>{t.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </Card>

      <Dialog open={openModal} onClose={() => setOpenModal(false)} PaperProps={{ sx: { bgcolor: c.dialogBg, border: `1px solid ${c.borderLight}`, borderRadius: 3, minWidth: 440 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>New Transaction</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>Product</InputLabel>
                <Select value={formData.product_id} label="Product" onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}>
                  {products.map(p => <MenuItem key={p.id} value={p.id}>{p.name} (Stock: {p.current_stock})</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Type</InputLabel>
                <Select value={formData.type} label="Type" onChange={(e) => setFormData({ ...formData, type: e.target.value })}>
                  {['purchase', 'sale', 'adjustment', 'return', 'transfer'].map(t => <MenuItem key={t} value={t} sx={{ textTransform: 'capitalize' }}>{t}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}><TextField fullWidth label="Quantity" type="number" value={formData.quantity} onChange={(e) => setFormData({ ...formData, quantity: e.target.value })} size="small" /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Unit Cost ($)" type="number" value={formData.unit_cost} onChange={(e) => setFormData({ ...formData, unit_cost: e.target.value })} size="small" /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Notes" multiline rows={2} value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} size="small" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setOpenModal(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={!formData.product_id || !formData.quantity} sx={{ background: 'linear-gradient(135deg, #6c63ff, #5a52d5)' }}>
            <SwapHoriz sx={{ mr: 1 }} /> Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
