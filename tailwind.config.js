/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        indigo: {
          50: '#f5f7ff',
          100: '#ebf0fe',
          200: '#ced9fb',
          300: '#adc0f7',
          400: '#8ba7f4',
          500: '#6a8df0',
          600: '#4874ed',
          700: '#275be9',
          800: '#1e47b2',
          900: '#15327b',
        }
      },
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
