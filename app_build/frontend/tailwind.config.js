/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: {
          DEFAULT: '#FAF5E9',
          50: '#FFFFFF',
          100: '#FAF5E9',
          200: '#F4ECD6',
          300: '#EDE2C2',
          400: '#E6D8AE',
          500: '#DFCE9A',
          card: '#F6EFE0',
          border: '#D8CCA8'
        },
        green: {
          brand: '#009B4D',
          dark: '#007A3D',
          light: '#E6F5ED'
        },
        tangerine: {
          DEFAULT: '#FFCC00',
          dark: '#E6B800',
          light: '#FFF8E1'
        },
        charcoal: {
          DEFAULT: '#111827',
          light: '#1F2937',
          border: '#374151'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
