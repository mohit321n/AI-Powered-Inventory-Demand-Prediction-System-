import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Alert, InputAdornment, IconButton, useTheme } from '@mui/material';
import { Visibility, VisibilityOff, Inventory, Email, Lock } from '@mui/icons-material';
import api from '../services/api';

export default function Login({ onLogin }) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const mutedColor = isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)';
  const iconColor = isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('token', res.data.token);
      onLogin();
      window.location.href = '/';
    } catch (err) {
      if (err.response && err.response.status === 401) {
        setError('Invalid email or password');
      } else {
        localStorage.setItem('token', 'demo-token');
        onLogin();
        window.location.href = '/';
      }
    }
    setLoading(false);
  };

  return (
    <Box className="login-container">
      <Box className="login-card fade-in">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box sx={{ width: 64, height: 64, borderRadius: 3, bgcolor: 'rgba(108,99,255,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
            <Inventory sx={{ fontSize: 36, color: '#6c63ff' }} />
          </Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>InvAI</Typography>
          <Typography variant="body2" color={mutedColor}>AI-Powered Inventory Management</Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            sx={{ mb: 2.5, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email sx={{ color: iconColor }} />
                </InputAdornment>
              ),
            }}
          />
          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock sx={{ color: iconColor }} />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" sx={{ color: iconColor }}>
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{
              py: 1.5,
              fontSize: 16,
              fontWeight: 600,
              background: 'linear-gradient(135deg, #6c63ff, #5a52d5)',
              boxShadow: '0 8px 24px rgba(108,99,255,0.3)',
              '&:hover': { background: 'linear-gradient(135deg, #7b73ff, #6c63ff)', boxShadow: '0 12px 32px rgba(108,99,255,0.4)' },
              '&:disabled': { background: 'rgba(108,99,255,0.3)' },
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="caption" color={iconColor}>
            Demo: Enter any email and password to login
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
