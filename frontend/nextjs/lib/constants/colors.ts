/**
 * Datadog Brand Colors
 * Based on official Datadog design system
 */

export const colors = {
  // Purple (Primary Brand)
  purple: {
    50: '#F5F3FF',
    100: '#EDE9FE',
    200: '#DDD6FE',
    300: '#C4B5FD',
    400: '#A78BFA',
    500: '#774AA4', // Datadog Purple
    600: '#632D91',
    700: '#4F217A',
    800: '#3B1663',
    900: '#270B4C',
  },

  // Accent Colors
  green: '#27AE60', // Success
  orange: '#F39C12', // Warning
  red: '#E74C3C', // Error
  blue: '#3498DB', // Info

  // Neutrals
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },

  // Background
  background: '#FAFAFA',
  surface: '#FFFFFF',
  border: '#E5E7EB',
} as const;

export const fonts = {
  sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
  mono: "'Fira Code', 'Courier New', monospace",
} as const;

export const fontSize = {
  xs: '0.75rem', // 12px
  sm: '0.875rem', // 14px
  base: '1rem', // 16px
  lg: '1.125rem', // 18px
  xl: '1.25rem', // 20px
  '2xl': '1.5rem', // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
} as const;

