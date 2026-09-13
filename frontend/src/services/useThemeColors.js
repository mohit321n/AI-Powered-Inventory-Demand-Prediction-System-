import { useTheme } from '@mui/material';

export default function useThemeColors() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  return {
    isDark,
    subtitle: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)',
    muted: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)',
    textPrimary: isDark ? '#fff' : 'rgba(0,0,0,0.87)',
    textSecondary: isDark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)',
    borderLight: isDark ? 'rgba(108,99,255,0.2)' : 'rgba(0,0,0,0.12)',
    inputBg: isDark ? 'rgba(108,99,255,0.05)' : 'rgba(0,0,0,0.02)',
    dialogBg: isDark ? '#1a1a2e' : '#ffffff',
  };
}
