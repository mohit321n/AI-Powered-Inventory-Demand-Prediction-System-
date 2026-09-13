import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, Button, Chip, IconButton, Grid, Badge } from '@mui/material';
import { Warning, Error, Info, CheckCircle, MarkEmailRead, Delete, FilterList } from '@mui/icons-material';
import api from '../services/api';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchAlerts(); }, []);

  const fetchAlerts = async () => {
    try {
      const res = await api.get('/alerts');
      setAlerts(res.data);
    } catch {
      setAlerts([
        { id: 1, type: 'low_stock', severity: 'high', title: 'Low Stock Alert', message: 'Monitor Light Bar has fallen below minimum stock level (28/50)', product: 'Monitor Light Bar', created_at: '2026-09-12T10:30:00', read: false },
        { id: 2, type: 'low_stock', severity: 'medium', title: 'Stock Warning', message: 'USB-C Hub is approaching minimum stock level (89/60)', product: 'USB-C Hub', created_at: '2026-09-12T08:15:00', read: false },
        { id: 3, type: 'demand_spike', severity: 'high', title: 'Demand Spike Detected', message: 'Unusual demand surge detected for Wireless Earbuds (+150% above average)', product: 'Wireless Earbuds', created_at: '2026-09-11T16:45:00', read: false },
        { id: 4, type: 'forecast', severity: 'info', title: 'Reorder Recommendation', message: 'AI recommends reordering 200 units of Smart Watch based on forecast', product: 'Smart Watch', created_at: '2026-09-11T14:20:00', read: true },
        { id: 5, type: 'seasonal', severity: 'medium', title: 'Seasonal Pattern', message: 'Laptop Stand sales typically increase 40% in September, consider early restock', product: 'Laptop Stand', created_at: '2026-09-10T11:30:00', read: true },
        { id: 6, type: 'anomaly', severity: 'high', title: 'Sales Anomaly', message: 'Unusual return rate detected for Mechanical Keyboard (15% in last 7 days)', product: 'Mechanical Keyboard', created_at: '2026-09-10T09:00:00', read: true },
        { id: 7, type: 'reorder', severity: 'low', title: 'Optimal Reorder Time', message: 'Based on lead times, now is the optimal time to reorder Yoga Mats', product: 'Yoga Mat', created_at: '2026-09-09T15:20:00', read: true },
        { id: 8, type: 'low_stock', severity: 'medium', title: 'Approaching Min Stock', message: 'Running Shoes stock (167) is nearing reorder point (30)', product: 'Running Shoes', created_at: '2026-09-09T10:00:00', read: true },
      ]);
    }
    setLoading(false);
  };

  const markAsRead = async (id) => {
    try {
      await api.patch(`/alerts/${id}/read`);
    } catch {}
    setAlerts(alerts.map(a => a.id === id ? { ...a, read: true } : a));
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/alerts/read-all');
    } catch {}
    setAlerts(alerts.map(a => ({ ...a, read: true })));
  };

  const deleteAlert = async (id) => {
    try {
      await api.delete(`/alerts/${id}`);
    } catch {}
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const getSeverityIcon = (severity) => {
    const icons = { high: <Error />, medium: <Warning />, low: <Info />, info: <Info /> };
    return icons[severity] || <Info />;
  };

  const getSeverityColor = (severity) => {
    const colors = { high: 'severity-high', medium: 'severity-medium', low: 'severity-low', info: 'severity-info' };
    return colors[severity] || 'severity-info';
  };

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !a.read;
    return a.severity === filter;
  });

  const unreadCount = alerts.filter(a => !a.read).length;

  return (
    <Box className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={700}>Alerts</Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.5)">
            {unreadCount > 0 ? `You have ${unreadCount} unread alert${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
          </Typography>
        </Box>
        {unreadCount > 0 && (
          <Button variant="outlined" startIcon={<MarkEmailRead />} onClick={markAllAsRead} sx={{ borderColor: 'rgba(108,99,255,0.3)', color: '#6c63ff' }}>
            Mark All Read
          </Button>
        )}
      </Box>

      <Card className="chart-card" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {[
            { key: 'all', label: 'All', count: alerts.length },
            { key: 'unread', label: 'Unread', count: unreadCount },
            { key: 'high', label: 'High', count: alerts.filter(a => a.severity === 'high').length },
            { key: 'medium', label: 'Medium', count: alerts.filter(a => a.severity === 'medium').length },
            { key: 'low', label: 'Low', count: alerts.filter(a => a.severity === 'low').length },
          ].map((f) => (
            <Button
              key={f.key}
              variant={filter === f.key ? 'contained' : 'outlined'}
              onClick={() => setFilter(f.key)}
              sx={{
                borderRadius: 3,
                textTransform: 'none',
                minWidth: 'auto',
                px: 2,
                bgcolor: filter === f.key ? 'rgba(108,99,255,0.2)' : 'transparent',
                borderColor: filter === f.key ? '#6c63ff' : 'rgba(108,99,255,0.2)',
                color: filter === f.key ? '#fff' : 'rgba(255,255,255,0.6)',
                '&:hover': { borderColor: '#6c63ff', bgcolor: 'rgba(108,99,255,0.1)' },
              }}
            >
              {f.label} ({f.count})
            </Button>
          ))}
        </Box>
      </Card>

      <Grid container spacing={2}>
        {filteredAlerts.map((alert, i) => (
          <Grid item xs={12} key={alert.id}>
            <Card
              className={`alert-card fade-in ${!alert.read ? 'unread' : ''}`}
              sx={{ animation: `fadeIn 0.4s ease-out ${i * 0.05}s both` }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                <Box sx={{ mt: 0.5, color: alert.severity === 'high' ? '#ff1744' : alert.severity === 'medium' ? '#ff9800' : '#00b0ff' }}>
                  {getSeverityIcon(alert.severity)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="subtitle1" fontWeight={600}>{alert.title}</Typography>
                    <span className={getSeverityColor(alert.severity)}>{alert.severity}</span>
                    {!alert.read && (
                      <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#6c63ff' }} />
                    )}
                  </Box>
                  <Typography variant="body2" color="rgba(255,255,255,0.6)" sx={{ mb: 1 }}>{alert.message}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Chip label={alert.product} size="small" sx={{ bgcolor: 'rgba(108,99,255,0.1)', color: '#6c63ff', fontSize: 11 }} />
                    <Typography variant="caption" color="rgba(255,255,255,0.3)">
                      {new Date(alert.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {!alert.read && (
                    <IconButton size="small" onClick={() => markAsRead(alert.id)} sx={{ color: '#6c63ff' }}>
                      <MarkEmailRead fontSize="small" />
                    </IconButton>
                  )}
                  <IconButton size="small" onClick={() => deleteAlert(alert.id)} sx={{ color: 'rgba(255,255,255,0.3)' }}>
                    <Delete fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredAlerts.length === 0 && (
        <Card className="chart-card" sx={{ textAlign: 'center', py: 6 }}>
          <CheckCircle sx={{ fontSize: 64, color: '#00c853', mb: 2 }} />
          <Typography variant="h6" color="rgba(255,255,255,0.5)">
            {filter === 'unread' ? 'All alerts have been read' : 'No alerts match this filter'}
          </Typography>
        </Card>
      )}
    </Box>
  );
}
