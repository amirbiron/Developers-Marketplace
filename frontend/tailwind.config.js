/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // רקעים כהים
        bg: "#0a0e12",
        surface: "#111820",
        surface2: "#0d141b",
        elevated: "#16202b",
        // גבולות
        line: "#1e2a36",
        "line-strong": "#2b3b4a",
        // טקסט
        ink: "#e6edf3",
        muted: "#8b98a5",
        faint: "#5b6b78",
        // אקסנט — ירוק טרמינל
        accent: {
          DEFAULT: "#10b981",
          bright: "#34d399",
          dim: "#0d9268",
          soft: "#065f46",
        },
        // צבעי סינטקס משניים (לגיוון אייקונים/תגיות)
        syntax: {
          cyan: "#38bdf8",
          violet: "#a78bfa",
          amber: "#fbbf24",
          rose: "#fb7185",
        },
      },
      fontFamily: {
        sans: ['"Heebo"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(16,185,129,0.35), 0 0 28px -6px rgba(16,185,129,0.45)",
        "glow-sm": "0 0 20px -8px rgba(16,185,129,0.55)",
        card: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 30px -12px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "accent-gradient": "linear-gradient(135deg, #34d399 0%, #10b981 45%, #0d9488 100%)",
        "dot-grid":
          "radial-gradient(circle at center, rgba(139,152,165,0.12) 1px, transparent 1px)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        blink: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0" } },
        "pulse-glow": {
          "0%,100%": { boxShadow: "0 0 20px -8px rgba(16,185,129,0.5)" },
          "50%": { boxShadow: "0 0 32px -4px rgba(16,185,129,0.75)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
        blink: "blink 1.1s step-end infinite",
        "pulse-glow": "pulse-glow 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
