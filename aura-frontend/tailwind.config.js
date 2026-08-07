/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aura: {
          dark: "#0b0f19",
          card: "#131b2e",
          cardHover: "#1c2842",
          accent: "#6366f1",
          accentHover: "#4f46e5",
          purple: "#a855f7",
          pink: "#ec4899",
          emerald: "#10b981",
          flac: "#f59e0b",
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in-fast': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 200ms ease-out',
        'fade-in-fast': 'fade-in-fast 150ms ease-out',
      },
    },
  },
  plugins: [],
}
