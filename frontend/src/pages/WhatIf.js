import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, Button, Grid, TextField, Switch, FormControlLabel, Slider, Select, MenuItem, FormControl, InputLabel, Divider, Chip, Alert, AlertTitle } from '@mui/material';
import { Science, TrendingUp, TrendingDown, Refresh, AutoAwesome } from '@mui/icons-material';
import api from '../services/api';

export default function WhatIf() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [scenarios, setScenarios] = useState({
    demandChange: 0,
    leadTimeChange: 0,
    promotionEnabled: false,
    safetyStockChange: 0,
    costChange: 0,
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);

  useEffect(() => { fetchProducts(); }, []);

  const fetchProducts = async () => {
    try {
      const res = await api.get('/products');
      setProducts(res.data);
    } catch {
      setProducts([
        { id: 1, name: 'Wireless Earbuds', current_stock: 245, min_stock: 50, max_stock: 500, price: 49.99, avg_daily_sales: 12 },
        { id: 2, name: 'Smart Watch', current_stock: 178, min_stock: 30, max_stock: 300, price: 199.99, avg_daily_sales: 8 },
        { id: 3, name: 'Laptop Stand', current_stock: 342, min_stock: 40, max_stock: 400, price: 29.99, avg_daily_sales: 15 },
        { id: 4, name: 'USB-C Hub', current_stock: 89, min_stock: 60, max_stock: 350, price: 34.99, avg_daily_sales: 10 },
        { id: 5, name: 'Mechanical Keyboard', current_stock: 156, min_stock: 45, max_stock: 250, price: 89.99, avg_daily_sales: 6 },
        { id: 6, name: 'Monitor Light Bar', current_stock: 28, min_stock: 50, max_stock: 200, price: 44.99, avg_daily_sales: 4 },
      ]);
    }
  };

  const runAnalysis = async () => {
    if (!selectedProduct) return;
    setLoading(true);
    try {
      const res = await api.post('/whatif/analyze', { product_id: selectedProduct, ...scenarios });
      setResults(res.data);
    } catch {
      const product = products.find(p => p.id === parseInt(selectedProduct));
      if (!product) return;

      const demandMultiplier = 1 + scenarios.demandChange / 100;
      const adjustedDemand = product.avg_daily_sales * demandMultiplier;
      const adjustedLeadTime = 7 + scenarios.leadTimeChange;
      const safetyStock = Math.max(0, product.min_stock + scenarios.safetyStockChange);
      const reorderPoint = Math.ceil(adjustedDemand * adjustedLeadTime + safetyStock);
      const economicOrderQty = Math.ceil(Math.sqrt(2 * adjustedDemand * 365 * 100 / (product.price * 0.2)));
      const daysUntilStockout = Math.floor(product.current_stock / adjustedDemand);
      const revenueImpact = scenarios.promotionEnabled ? adjustedDemand * product.price * 0.15 * 30 : 0;
      const stockoutRisk = daysUntilStockout < adjustedLeadTime + 3 ? 'High' : daysUntilStockout < adjustedLeadTime + 7 ? 'Medium' : 'Low';
      const recommendedAction = stockoutRisk === 'High' ? 'Immediate reorder required' : stockoutRisk === 'Medium' ? 'Schedule reorder within 3 days' : 'Stock levels are adequate';

      setResults({
        product: product.name,
        current_stock: product.current_stock,
        adjusted_daily_demand: adjustedDemand.toFixed(1),
        days_until_stockout: daysUntilStockout,
        reorder_point: reorderPoint,
        economic_order_qty: economicOrderQty,
        safety_stock_level: safetyStock,
        stockout_risk: stockoutRisk,
        recommended_order_quantity: reorderPoint - product.current_stock + economicOrderQty,
        revenue_impact_30d: revenueImpact.toFixed(2),
        promotion_impact: scenarios.promotionEnabled ? `+${(demandMultiplier * 15 - 15).toFixed(1)}% demand lift` : 'No promotion active',
        recommended_action: recommendedAction,
        cost_per_unit: (product.price * (1 + scenarios.costChange / 100)).toFixed(2),
      });
    }
    setAnalyzed(true);
    setLoading(false);
  };

  const resetScenarios = () => {
    setScenarios({ demandChange: 0, leadTimeChange: 0, promotionEnabled: false, safetyStockChange: 0, costChange: 0 });
    setResults(null);
    setAnalyzed(false);
  };

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>What-If Analysis</Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.5)">Simulate scenarios to optimize inventory decisions</Typography>
        </Box>
        <Button variant="outlined" onClick={resetScenarios} sx={{ borderColor: 'rgba(108,99,255,0.3)', color: '#6c63ff' }}>
          <Refresh sx={{ mr: 1 }} /> Reset
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Card className="scenario-card" sx={{ height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <Science sx={{ color: '#6c63ff' }} />
              <Typography variant="h6">Scenario Parameters</Typography>
            </Box>

            <FormControl fullWidth size="small" sx={{ mb: 3 }}>
              <InputLabel>Select Product</InputLabel>
              <Select value={selectedProduct} label="Select Product" onChange={(e) => setSelectedProduct(e.target.value)}>
                {products.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
              </Select>
            </FormControl>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" fontWeight={500}>Demand Change</Typography>
                <Chip label={`${scenarios.demandChange > 0 ? '+' : ''}${scenarios.demandChange}%`} size="small" sx={{ bgcolor: scenarios.demandChange > 0 ? 'rgba(0,200,83,0.15)' : scenarios.demandChange < 0 ? 'rgba(255,23,68,0.15)' : 'rgba(255,255,255,0.08)', color: scenarios.demandChange > 0 ? '#00c853' : scenarios.demandChange < 0 ? '#ff1744' : '#fff', fontWeight: 600 }} />
              </Box>
              <Slider value={scenarios.demandChange} onChange={(e, v) => setScenarios({ ...scenarios, demandChange: v })} min={-50} max={100} step={5} sx={{ color: '#6c63ff' }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption" color="rgba(255,255,255,0.3)">-50%</Typography>
                <Typography variant="caption" color="rgba(255,255,255,0.3)">+100%</Typography>
              </Box>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" fontWeight={500}>Lead Time Change</Typography>
                <Chip label={`${scenarios.leadTimeChange > 0 ? '+' : ''}${scenarios.leadTimeChange} days`} size="small" sx={{ bgcolor: scenarios.leadTimeChange > 0 ? 'rgba(255,152,0,0.15)' : scenarios.leadTimeChange < 0 ? 'rgba(0,200,83,0.15)' : 'rgba(255,255,255,0.08)', color: scenarios.leadTimeChange > 0 ? '#ff9800' : scenarios.leadTimeChange < 0 ? '#00c853' : '#fff', fontWeight: 600 }} />
              </Box>
              <Slider value={scenarios.leadTimeChange} onChange={(e, v) => setScenarios({ ...scenarios, leadTimeChange: v })} min={-5} max={14} step={1} sx={{ color: '#ff9800' }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption" color="rgba(255,255,255,0.3)">-5 days</Typography>
                <Typography variant="caption" color="rgba(255,255,255,0.3)">+14 days</Typography>
              </Box>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" fontWeight={500}>Safety Stock Change</Typography>
                <Chip label={`${scenarios.safetyStockChange > 0 ? '+' : ''}${scenarios.safetyStockChange}`} size="small" sx={{ bgcolor: 'rgba(0,176,255,0.15)', color: '#00b0ff', fontWeight: 600 }} />
              </Box>
              <Slider value={scenarios.safetyStockChange} onChange={(e, v) => setScenarios({ ...scenarios, safetyStockChange: v })} min={-30} max={100} step={5} sx={{ color: '#00b0ff' }} />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" fontWeight={500}>Cost Change</Typography>
                <Chip label={`${scenarios.costChange > 0 ? '+' : ''}${scenarios.costChange}%`} size="small" sx={{ bgcolor: 'rgba(255,101,132,0.15)', color: '#ff6584', fontWeight: 600 }} />
              </Box>
              <Slider value={scenarios.costChange} onChange={(e, v) => setScenarios({ ...scenarios, costChange: v })} min={-30} max={50} step={5} sx={{ color: '#ff6584' }} />
            </Box>

            <FormControlLabel
              control={<Switch checked={scenarios.promotionEnabled} onChange={(e) => setScenarios({ ...scenarios, promotionEnabled: e.target.checked })} sx={{ '& .MuiSwitch-switchBase.Mui-checked': { color: '#6c63ff' }, '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { bgcolor: '#6c63ff' } }} />}
              label={<Typography variant="body2" fontWeight={500}>Enable Promotion Campaign</Typography>}
              sx={{ mb: 3 }}
            />

            <Button
              variant="contained"
              fullWidth
              onClick={runAnalysis}
              disabled={!selectedProduct || loading}
              sx={{ background: 'linear-gradient(135deg, #6c63ff, #ff6584)', py: 1.5, fontSize: 16 }}
            >
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </Button>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          {analyzed && results ? (
            <Card className="scenario-card slide-up">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <AutoAwesome sx={{ color: '#ff9800' }} />
                <Typography variant="h6">Analysis Results</Typography>
                <Chip label={results.product} size="small" sx={{ bgcolor: 'rgba(108,99,255,0.15)', color: '#6c63ff', ml: 'auto' }} />
              </Box>

              <Alert severity={results.stockout_risk === 'High' ? 'error' : results.stockout_risk === 'Medium' ? 'warning' : 'success'} sx={{ mb: 3, bgcolor: results.stockout_risk === 'High' ? 'rgba(255,23,68,0.1)' : results.stockout_risk === 'Medium' ? 'rgba(255,152,0,0.1)' : 'rgba(0,200,83,0.1)', border: 'none', '& .MuiAlert-icon': { color: results.stockout_risk === 'High' ? '#ff1744' : results.stockout_risk === 'Medium' ? '#ff9800' : '#00c853' } }}>
                <AlertTitle>{results.recommended_action}</AlertTitle>
                Stockout Risk: {results.stockout_risk} | Days until stockout: {results.days_until_stockout}
              </Alert>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                {[
                  { label: 'Adjusted Daily Demand', value: results.adjusted_daily_demand, color: '#6c63ff' },
                  { label: 'Days Until Stockout', value: `${results.days_until_stockout}d`, color: results.days_until_stockout < 14 ? '#ff1744' : '#00c853' },
                  { label: 'Reorder Point', value: results.reorder_point, color: '#ff9800' },
                  { label: 'Order Quantity (EOQ)', value: results.economic_order_qty, color: '#00b0ff' },
                  { label: 'Safety Stock Level', value: results.safety_stock_level, color: '#ff6584' },
                  { label: 'Recommended Order', value: results.recommended_order_quantity, color: '#6c63ff' },
                ].map((item, i) => (
                  <Grid item xs={6} sm={4} key={i}>
                    <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'rgba(108,99,255,0.05)', border: '1px solid rgba(108,99,255,0.1)' }}>
                      <Typography variant="caption" color="rgba(255,255,255,0.5)">{item.label}</Typography>
                      <Typography variant="h6" fontWeight={700} color={item.color}>{item.value}</Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              <Divider sx={{ borderColor: 'rgba(108,99,255,0.1)', my: 2 }} />

              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip label={`Cost per unit: $${results.cost_per_unit}`} sx={{ bgcolor: 'rgba(255,101,132,0.1)', color: '#ff6584' }} />
                <Chip label={`Promotion: ${results.promotion_impact}`} sx={{ bgcolor: 'rgba(108,99,255,0.1)', color: '#6c63ff' }} />
                <Chip label={`30d Revenue Impact: ${parseFloat(results.revenue_impact_30d) >= 0 ? '+' : ''}$${results.revenue_impact_30d}`} sx={{ bgcolor: parseFloat(results.revenue_impact_30d) >= 0 ? 'rgba(0,200,83,0.1)' : 'rgba(255,23,68,0.1)', color: parseFloat(results.revenue_impact_30d) >= 0 ? '#00c853' : '#ff1744' }} />
              </Box>
            </Card>
          ) : (
            <Card className="scenario-card" sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', py: 8 }}>
              <Box>
                <Science sx={{ fontSize: 80, color: 'rgba(108,99,255,0.2)', mb: 2 }} />
                <Typography variant="h6" color="rgba(255,255,255,0.4)">Configure parameters and run analysis</Typography>
                <Typography variant="body2" color="rgba(255,255,255,0.25)">Adjust sliders to simulate different scenarios</Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
