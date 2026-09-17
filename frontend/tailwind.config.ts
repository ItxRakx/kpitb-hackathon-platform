import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
        accent: {
          50: "#fdf4ff",
          100: "#fae8ff",
          200: "#f5d0fe",
          300: "#f0abfc",
          400: "#e879f9",
          500: "#d946ef",
          600: "#c026d3",
          700: "#a21caf",
          800: "#86198f",
          900: "#701a75",
        },
        surface: {
          DEFAULT: "#ffffff",
          dark: "#0b1020",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 10px 30px -12px rgba(30, 64, 175, 0.2)",
        glow: "0 0 0 1px rgba(59,130,246,0.15), 0 20px 60px -20px rgba(59,130,246,0.45)",
      },
      backgroundImage: {
        "hero-gradient":
          "radial-gradient(1200px 600px at 10% -10%, rgba(59,130,246,0.25), transparent 60%), radial-gradient(800px 400px at 110% 10%, rgba(217,70,239,0.22), transparent 60%), linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)",
        "hero-gradient-dark":
          "radial-gradient(1200px 600px at 10% -10%, rgba(59,130,246,0.25), transparent 60%), radial-gradient(800px 400px at 110% 10%, rgba(217,70,239,0.22), transparent 60%), linear-gradient(180deg, #0b1020 0%, #0f172a 100%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out both",
      },
    },
  },
  plugins: [],
} satisfies Config;
