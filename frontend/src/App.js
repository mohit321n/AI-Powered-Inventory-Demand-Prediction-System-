import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, Drawer, AppBar, Toolbar, Typography, List, ListItem, ListItemIcon, ListItemText, IconButton, Avatar, Menu, MenuItem, Badge, useMediaQuery, Tooltip } from '@mui/material';
import { Menu as MenuIcon, Dashboard as DashboardIcon, Inventory as InventoryIcon, ShoppingCart as SalesIcon, TrendingUp as ForecastIcon, Warning as AlertIcon, Science as WhatIfIcon, Category as ProductsIcon, AccountCircle, Logout, ChevronLeft, DarkMode, LightMode } from '@mui/icons-material';

import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import Sales from './pages/Sales';
import Forecast from './pages/Forecast';
import Alerts from './pages/Alerts';
import WhatIf from './pages/WhatIf';
import Login from './pages/Login';

const ThemeModeContext = createContext();

const sharedComponents = {
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 8, fontWeight: 600 },
      },
    },
  },
};

const darkTheme = createTheme({
  ...sharedComponents,
  palette: {
    mode: 'dark',
    primary: { main: '#6c63ff' },
    secondary: { main: '#ff6584' },
    background: { default: '#0f0f23', paper: '#1a1a2e' },
    success: { main: '#00c853' },
    warning: { main: '#ff9800' },
    error: { main: '#ff1744' },
    info: { main: '#00b0ff' },
  },
  components: {
    ...sharedComponents.components,
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #1a1a2e 0%, #16213e 100%)',
          border: '1px solid rgba(108, 99, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: '1px solid rgba(108, 99, 255, 0.1)' },
      },
    },
  },
});

const lightTheme = createTheme({
  ...sharedComponents,
  palette: {
    mode: 'light',
    primary: { main: '#6c63ff' },
    secondary: { main: '#ff6584' },
    background: { default: '#f0f2f5', paper: '#ffffff' },
    success: { main: '#00c853' },
    warning: { main: '#ff9800' },
    error: { main: '#ff1744' },
    info: { main: '#00b0ff' },
    text: { primary: '#1a1a2e', secondary: '#555' },
  },
  components: {
    ...sharedComponents.components,
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#ffffff',
          border: '1px solid rgba(108, 99, 255, 0.12)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: '1px solid rgba(0,0,0,0.08)' },
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

function Sidebar({ open, onClose, mobileOpen, onMobileClose, mode }) {
  const location = useLocation();
  const isMobile = useMediaQuery('(max-width:900px)');
  const isDark = mode === 'dark';

  const sidebarBg = isDark ? '#0a0a1a' : '#ffffff';
  const textColor = isDark ? 'rgba(255,255,255,0.87)' : 'rgba(0,0,0,0.87)';
  const mutedColor = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)';
  const borderColor = isDark ? 'rgba(108, 99, 255, 0.1)' : 'rgba(108, 99, 255, 0.12)';
  const activeBg = isDark ? 'rgba(108, 99, 255, 0.2)' : 'rgba(108, 99, 255, 0.1)';
  const hoverBg = isDark ? 'rgba(108, 99, 255, 0.1)' : 'rgba(108, 99, 255, 0.06)';
  const activeText = isDark ? '#fff' : '#6c63ff';

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
          <InventoryIcon />
        </Avatar>
        <Box>
          <Typography variant="subtitle1" fontWeight={700} color={textColor}>InvAI</Typography>
          <Typography variant="caption" color={mutedColor}>Smart Inventory</Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={onMobileClose} sx={{ ml: 'auto', color: mutedColor }}>
            <ChevronLeft />
          </IconButton>
        )}
      </Box>
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="caption" sx={{ color: mutedColor, textTransform: 'uppercase', letterSpacing: 1, fontSize: 10 }}>Navigation</Typography>
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
                borderRadius: 2, mb: 0.5, mx: 0.5,
                backgroundColor: isActive ? activeBg : 'transparent',
                borderLeft: isActive ? '3px solid #6c63ff' : '3px solid transparent',
                '&:hover': { backgroundColor: hoverBg },
                transition: 'all 0.2s',
              }}
            >
              <ListItemIcon sx={{ color: isActive ? '#6c63ff' : mutedColor, minWidth: 40 }}>
                {item.badge ? <Badge badgeContent="!" color="error">{item.icon}</Badge> : item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ fontSize: 14, fontWeight: isActive ? 600 : 400, color: isActive ? activeText : textColor }} />
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ p: 2, borderTop: `1px solid ${borderColor}` }}>
        <Box sx={{ p: 1.5, borderRadius: 2, background: isDark ? 'linear-gradient(135deg, rgba(108,99,255,0.2), rgba(255,101,132,0.2))' : 'linear-gradient(135deg, rgba(108,99,255,0.08), rgba(255,101,132,0.08))', border: `1px solid ${borderColor}` }}>
          <Typography variant="caption" color={textColor} fontWeight={600}>AI Engine</Typography>
          <Typography variant="caption" display="block" color={mutedColor} fontSize={10}>Demand forecasting active</Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, bgcolor: sidebarBg, borderRight: `1px solid ${borderColor}`, boxSizing: 'border-box' },
        }}
        open={open}
      >
        {drawerContent}
      </Drawer>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, bgcolor: sidebarBg, borderRight: `1px solid ${borderColor}` },
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
}

function Layout({ children, mode, toggleMode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const isDark = mode === 'dark';

  const appBarBg = isDark ? 'rgba(15, 15, 35, 0.9)' : 'rgba(255, 255, 255, 0.9)';
  const appBarBorder = isDark ? '1px solid rgba(108, 99, 255, 0.1)' : '1px solid rgba(0,0,0,0.08)';
  const appBarColor = isDark ? '#fff' : '#1a1a2e';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Sidebar open={true} onClose={() => {}} mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} mode={mode} />
      <Box component="main" sx={{ flexGrow: 1, ml: { md: `${DRAWER_WIDTH}px` }, display: 'flex', flexDirection: 'column' }}>
        <AppBar position="sticky" elevation={0} sx={{ bgcolor: appBarBg, backdropFilter: 'blur(20px)', borderBottom: appBarBorder }}>
          <Toolbar>
            <IconButton color="inherit" edge="start" onClick={() => setMobileOpen(true)} sx={{ display: { md: 'none' }, mr: 2, color: appBarColor }}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600, color: appBarColor }}>
              AI Inventory Management
            </Typography>
            <Tooltip title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
              <IconButton onClick={toggleMode} sx={{ color: appBarColor, mr: 1 }}>
                {isDark ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ color: appBarColor }}>
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
  const [mode, setMode] = useState(() => localStorage.getItem('themeMode') || 'dark');

  const toggleMode = () => {
    const newMode = mode === 'dark' ? 'light' : 'dark';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  useEffect(() => {
    const handleStorage = () => setIsAuthenticated(!!localStorage.getItem('token'));
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const theme = mode === 'dark' ? darkTheme : lightTheme;

  return (
    <ThemeModeContext.Provider value={{ mode, toggleMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
            <Route path="/*" element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout mode={mode} toggleMode={toggleMode}>
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
    </ThemeModeContext.Provider>
  );
}

export { ThemeModeContext };
