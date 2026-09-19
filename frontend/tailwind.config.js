/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
    "./data/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        red: {
          50: "#eef3fb",
          100: "#dbe6f5",
          200: "#b8cbe8",
          300: "#8da9d1",
          400: "#5f83b5",
          500: "#315d91",
          600: "#244a7a",
          700: "#1b3a63",
          800: "#142f52",
          900: "#0d2340",
          950: "#08182d",
        },
      },
    },
  },
  plugins: [],
};
