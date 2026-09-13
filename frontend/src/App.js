import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, Drawer, AppBar, Toolbar, Typography, List, ListItem, ListItemIcon, ListItemText, IconButton, Avatar, Menu, MenuItem, Badge, useMediaQuery } from '@mui/material';
import { Menu as MenuIcon, Dashboard as DashboardIcon, Inventory as InventoryIcon, ShoppingCart as SalesIcon, TrendingUp as ForecastIcon, Warning as AlertIcon, Science as WhatIfIcon, Category as ProductsIcon, AccountCircle, Logout, ChevronLeft } from '@mui/icons-material';

import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import Sales from './pages/Sales';
import Forecast from './pages/Forecast';
import Alerts from './pages/Alerts';
import WhatIf from './pages/WhatIf';
import Login from './pages/Login';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6c63ff' },
    secondary: { main: '#ff6584' },
    background: {
      default: '#0f0f23',
      paper: '#1a1a2e',
    },
    success: { main: '#00c853' },
    warning: { main: '#ff9800' },
    error: { main: '#ff1744' },
    info: { main: '#00b0ff' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #1a1a2e 0%, #16213e 100%)',
          border: '1px solid rgba(108, 99, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 600,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(108, 99, 255, 0.1)',
        },
      },
    },
  },
});

const DRAWER_WIDTH = 260;

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Products', icon: <ProductsIcon />, path: '/products' },
  { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory' },
  { text: 'Sales', icon: <SalesIcon />, path: '/sales' },
  { text: 'Forecast', icon: <ForecastIcon />, path: '/forecast' },
  { text: 'Alerts', icon: <AlertIcon />, path: '/alerts', badge: true },
  { text: 'What-If Analysis', icon: <WhatIfIcon />, path: '/whatif' },
];

function ProtectedRoute({ children, isAuthenticated }) {
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function Sidebar({ open, onClose, mobileOpen, onMobileClose }) {
  const location = useLocation();
  const isMobile = useMediaQuery('(max-width:900px)');

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
          <InventoryIcon />
        </Avatar>
        <Box>
          <Typography variant="subtitle1" fontWeight={700} color="white">InvAI</Typography>
          <Typography variant="caption" color="rgba(255,255,255,0.5)">Smart Inventory</Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={onMobileClose} sx={{ ml: 'auto', color: 'rgba(255,255,255,0.5)' }}>
            <ChevronLeft />
          </IconButton>
        )}
      </Box>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: 1, fontSize: 10 }}>Navigation</Typography>
      </Box>
      <List sx={{ flex: 1, px: 1 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem
              key={item.text}
              component={Link}
              to={item.path}
              onClick={isMobile ? onMobileClose : undefined}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                mx: 0.5,
                backgroundColor: isActive ? 'rgba(108, 99, 255, 0.2)' : 'transparent',
                borderLeft: isActive ? '3px solid #6c63ff' : '3px solid transparent',
                '&:hover': { backgroundColor: 'rgba(108, 99, 255, 0.1)' },
                transition: 'all 0.2s',
              }}
            >
              <ListItemIcon sx={{ color: isActive ? '#6c63ff' : 'rgba(255,255,255,0.5)', minWidth: 40 }}>
                {item.badge ? (
                  <Badge badgeContent="!" color="error">{item.icon}</Badge>
                ) : item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ fontSize: 14, fontWeight: isActive ? 600 : 400, color: isActive ? '#fff' : 'rgba(255,255,255,0.7)' }} />
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ p: 2, borderTop: '1px solid rgba(108, 99, 255, 0.1)' }}>
        <Box sx={{ p: 1.5, borderRadius: 2, background: 'linear-gradient(135deg, rgba(108,99,255,0.2), rgba(255,101,132,0.2))', border: '1px solid rgba(108, 99, 255, 0.2)' }}>
          <Typography variant="caption" color="rgba(255,255,255,0.7)" fontWeight={600}>AI Engine</Typography>
          <Typography variant="caption" display="block" color="rgba(255,255,255,0.4)" fontSize={10}>Demand forecasting active</Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <>
      {/* Desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            bgcolor: '#0a0a1a',
            borderRight: '1px solid rgba(108, 99, 255, 0.1)',
            boxSizing: 'border-box',
          },
        }}
        open={open}
      >
        {drawerContent}
      </Drawer>
      {/* Mobile */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            bgcolor: '#0a0a1a',
            borderRight: '1px solid rgba(108, 99, 255, 0.1)',
          },
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
}

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Sidebar open={true} onClose={() => {}} mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
      <Box component="main" sx={{ flexGrow: 1, ml: { md: `${DRAWER_WIDTH}px` }, display: 'flex', flexDirection: 'column' }}>
        <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'rgba(15, 15, 35, 0.9)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(108, 99, 255, 0.1)' }}>
          <Toolbar>
            <IconButton color="inherit" edge="start" onClick={() => setMobileOpen(true)} sx={{ display: { md: 'none' }, mr: 2 }}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
              AI Inventory Management
            </Typography>
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} color="inherit">
              <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem onClick={() => setAnchorEl(null)}><AccountCircle sx={{ mr: 1 }} /> Profile</MenuItem>
              <MenuItem onClick={() => { localStorage.removeItem('token'); window.location.href = '/login'; }}><Logout sx={{ mr: 1 }} /> Logout</MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        <Box sx={{ p: { xs: 2, md: 3 }, flex: 1 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

  useEffect(() => {
    const handleStorage = () => setIsAuthenticated(!!localStorage.getItem('token'));
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
          <Route path="/*" element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/products" element={<Products />} />
                  <Route path="/inventory" element={<Inventory />} />
                  <Route path="/sales" element={<Sales />} />
                  <Route path="/forecast" element={<Forecast />} />
                  <Route path="/alerts" element={<Alerts />} />
                  <Route path="/whatif" element={<WhatIf />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}
