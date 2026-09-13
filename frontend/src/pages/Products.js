import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, Button, TextField, Select, MenuItem, FormControl, InputLabel, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, Chip, Grid, InputAdornment } from '@mui/material';
import { Add, Edit, Delete, Search, FilterList } from '@mui/icons-material';
import api from '../services/api';
import useThemeColors from '../services/useThemeColors';

export default function Products() {
  const c = useThemeColors();
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [categories, setCategories] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({ name: '', sku: '', category: '', price: '', cost: '', description: '', min_stock: '', max_stock: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchProducts(); }, []);

  useEffect(() => {
    let result = products;
    if (search) result = result.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.sku.toLowerCase().includes(search.toLowerCase()));
    if (categoryFilter !== 'all') result = result.filter(p => p.category === categoryFilter);
    setFilteredProducts(result);
  }, [products, search, categoryFilter]);

  const fetchProducts = async () => {
    try {
      const res = await api.get('/products');
      setProducts(res.data);
      setCategories([...new Set(res.data.map(p => p.category))]);
    } catch {
      const mock = [
        { id: 1, name: 'Wireless Earbuds', sku: 'WE-001', category: 'Electronics', price: 49.99, cost: 12.50, min_stock: 50, max_stock: 500, current_stock: 245 },
        { id: 2, name: 'Smart Watch', sku: 'SW-002', category: 'Electronics', price: 199.99, cost: 45.00, min_stock: 30, max_stock: 300, current_stock: 178 },
        { id: 3, name: 'Laptop Stand', sku: 'LS-003', category: 'Accessories', price: 29.99, cost: 8.00, min_stock: 40, max_stock: 400, current_stock: 342 },
        { id: 4, name: 'USB-C Hub', sku: 'UH-004', category: 'Accessories', price: 34.99, cost: 10.00, min_stock: 60, max_stock: 350, current_stock: 89 },
        { id: 5, name: 'Mechanical Keyboard', sku: 'MK-005', category: 'Electronics', price: 89.99, cost: 22.00, min_stock: 45, max_stock: 250, current_stock: 156 },
        { id: 6, name: 'Monitor Light Bar', sku: 'ML-006', category: 'Accessories', price: 44.99, cost: 15.00, min_stock: 50, max_stock: 200, current_stock: 28 },
        { id: 7, name: 'Running Shoes', sku: 'RS-007', category: 'Sports', price: 129.99, cost: 35.00, min_stock: 30, max_stock: 200, current_stock: 167 },
        { id: 8, name: 'Yoga Mat', sku: 'YM-008', category: 'Sports', price: 39.99, cost: 11.00, min_stock: 40, max_stock: 300, current_stock: 234 },
      ];
      setProducts(mock);
      setCategories([...new Set(mock.map(p => p.category))]);
    }
    setLoading(false);
  };

  const handleOpenModal = (product = null) => {
    if (product) {
      setEditingProduct(product);
      setFormData({ name: product.name, sku: product.sku, category: product.category, price: product.price.toString(), cost: product.cost.toString(), description: product.description || '', min_stock: product.min_stock.toString(), max_stock: product.max_stock.toString() });
    } else {
      setEditingProduct(null);
      setFormData({ name: '', sku: '', category: '', price: '', cost: '', description: '', min_stock: '', max_stock: '' });
    }
    setOpenModal(true);
  };

  const handleCloseModal = () => { setOpenModal(false); setEditingProduct(null); };

  const handleSubmit = async () => {
    try {
      const payload = { ...formData, price: parseFloat(formData.price), cost: parseFloat(formData.cost), min_stock: parseInt(formData.min_stock), max_stock: parseInt(formData.max_stock) };
      if (editingProduct) {
        await api.put(`/products/${editingProduct.id}`, payload);
      } else {
        await api.post('/products', payload);
      }
      fetchProducts();
      handleCloseModal();
    } catch {
      if (editingProduct) {
        setProducts(products.map(p => p.id === editingProduct.id ? { ...p, ...payload, id: p.id } : p));
      } else {
        setProducts([...products, { ...payload, id: Date.now(), current_stock: 0 }]);
      }
      handleCloseModal();
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await api.delete(`/products/${id}`);
        fetchProducts();
      } catch {
        setProducts(products.filter(p => p.id !== id));
      }
    }
  };

  const getStockStatus = (current, min, max) => {
    if (current <= min * 0.5) return { label: 'Critical', className: 'status-critical' };
    if (current <= min) return { label: 'Low', className: 'status-low' };
    if (current >= max * 0.9) return { label: 'High', className: 'status-active' };
    return { label: 'Normal', className: 'status-active' };
  };

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Products</Typography>
          <Typography variant="body2" color={c.subtitle}>Manage your product catalog</Typography>
        </Box>
        <Button variant="contained" startIcon={<Add />} onClick={() => handleOpenModal()} sx={{ background: 'linear-gradient(135deg, #6c63ff, #5a52d5)', px: 3 }}>
          Add Product
        </Button>
      </Box>

      <Card className="chart-card" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { borderRadius: 2, bgcolor: c.inputBg } }}
            InputProps={{ startAdornment: <InputAdornment position="start"><Search sx={{ color: c.muted }} /></InputAdornment> }}
          />
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Category</InputLabel>
            <Select value={categoryFilter} label="Category" onChange={(e) => setCategoryFilter(e.target.value)} sx={{ borderRadius: 2 }}>
              <MenuItem value="all">All Categories</MenuItem>
              {categories.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </Select>
          </FormControl>
        </Box>
      </Card>

      <Card className="chart-card">
        <Box sx={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Price</th>
                <th>Cost</th>
                <th>Stock</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map((product) => {
                const status = getStockStatus(product.current_stock || 0, product.min_stock, product.max_stock);
                return (
                  <tr key={product.id}>
                    <td style={{ fontWeight: 500 }}>{product.name}</td>
                    <td><Chip label={product.sku} size="small" sx={{ bgcolor: 'rgba(108,99,255,0.1)', color: '#6c63ff', fontSize: 11 }} /></td>
                    <td>{product.category}</td>
                    <td style={{ color: '#00c853' }}>₹{product.price.toFixed(2)}</td>
                    <td>₹{product.cost.toFixed(2)}</td>
                    <td>{product.current_stock || 0} / {product.max_stock}</td>
                    <td><span className={`status-badge ${status.className}`}>{status.label}</span></td>
                    <td>
                      <IconButton size="small" onClick={() => handleOpenModal(product)} sx={{ color: '#6c63ff' }}><Edit fontSize="small" /></IconButton>
                      <IconButton size="small" onClick={() => handleDelete(product.id)} sx={{ color: '#ff6584' }}><Delete fontSize="small" /></IconButton>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Box>
      </Card>

      <Dialog open={openModal} onClose={handleCloseModal} PaperProps={{ sx: { bgcolor: c.dialogBg, border: `1px solid ${c.borderLight}`, borderRadius: 3, minWidth: 480 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>{editingProduct ? 'Edit Product' : 'Add New Product'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}><TextField fullWidth label="Product Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} size="small" /></Grid>
            <Grid item xs={6}><TextField fullWidth label="SKU" value={formData.sku} onChange={(e) => setFormData({ ...formData, sku: e.target.value })} size="small" /></Grid>
            <Grid item xs={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select value={formData.category} label="Category" onChange={(e) => setFormData({ ...formData, category: e.target.value })}>
                  {['Electronics', 'Accessories', 'Sports', 'Home & Garden', 'Clothing', 'Books'].map(cat => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}><TextField fullWidth label="Price" type="number" value={formData.price} onChange={(e) => setFormData({ ...formData, price: e.target.value })} size="small" /></Grid>
            <Grid item xs={6}><TextField fullWidth label="Cost" type="number" value={formData.cost} onChange={(e) => setFormData({ ...formData, cost: e.target.value })} size="small" /></Grid>
            <Grid item xs={6}><TextField fullWidth label="Min Stock" type="number" value={formData.min_stock} onChange={(e) => setFormData({ ...formData, min_stock: e.target.value })} size="small" /></Grid>
            <Grid item xs={6}><TextField fullWidth label="Max Stock" type="number" value={formData.max_stock} onChange={(e) => setFormData({ ...formData, max_stock: e.target.value })} size="small" /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Description" multiline rows={2} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} size="small" /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={handleCloseModal}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={!formData.name || !formData.price} sx={{ background: 'linear-gradient(135deg, #6c63ff, #5a52d5)' }}>
            {editingProduct ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
