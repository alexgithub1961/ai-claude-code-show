/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        hhg: {
          primary: '#0066CC',
          secondary: '#FF6B35',
          dark: '#1a1a1a',
          light: '#f5f5f5',
        }
      }
    },
  },
  plugins: [],
}
