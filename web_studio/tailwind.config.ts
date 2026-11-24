import type { Config } from 'tailwindcss';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        studio: {
          bg: '#0F1117',
          card: '#171A23',
          elevated: '#1E2230',
          border: '#262B38',
          text: '#E6E8EE',
          muted: '#8B93A7',
          purple: '#7C5CFF',
          blue: '#4F8CFF',
          success: '#2ECC71',
          warning: '#F5A524',
          error: '#FF5C5C',
        },
      },
      borderRadius: {
        studio: '12px',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(95deg, #7C5CFF 0%, #4F8CFF 100%)',
      },
    },
  },
  plugins: [],
} satisfies Config;
