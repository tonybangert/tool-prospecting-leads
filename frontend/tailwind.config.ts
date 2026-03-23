import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#102d50",
          light: "#1a3f6b",
          dark: "#0b1f38",
          bg: "#f0f4f8",
        },
        amber: {
          DEFAULT: "#faa840",
          light: "#fbc06c",
          dark: "#d48c2a",
          bg: "#fff8ec",
        },
        coral: {
          DEFAULT: "#ef4537",
          light: "#f47268",
          bg: "#fef0ef",
        },
        primary: { DEFAULT: "#102d50", light: "#1a3f6b", bg: "#f0f4f8" },
        accent: { DEFAULT: "#faa840", bg: "#fff8ec" },
        success: { DEFAULT: "#10b981", bg: "#ecfdf5" },
        warning: { DEFAULT: "#f59e0b", bg: "#fffbeb" },
        danger: { DEFAULT: "#ef4537", bg: "#fef0ef" },
        dark: { DEFAULT: "#102d50", surface: "#1a3f6b", border: "#2a4a6b" },
        surface: "#ffffff",
        bg: "#f5f7fa",
        muted: "#6b7280",
        "text-light": "#9ca3af",
        status: {
          discovered: "#faa840",
          selected: "#3b82f6",
          enriched: "#10b981",
          scored: "#7c3aed",
        },
        risk: { low: "#10b981", medium: "#f59e0b", high: "#ef4537" },
      },
      fontFamily: {
        mono: [
          "SF Mono",
          "Cascadia Code",
          "Fira Code",
          "Consolas",
          "Courier New",
          "monospace",
        ],
      },
      borderRadius: {
        DEFAULT: "10px",
        sm: "6px",
      },
      boxShadow: {
        DEFAULT:
          "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        md: "0 4px 6px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.03)",
      },
      maxWidth: {
        container: "1400px",
      },
      keyframes: {
        "ticker-scroll": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "ticker-scroll": "ticker-scroll 30s linear infinite",
        "fade-in": "fade-in 0.3s ease-out",
        shimmer: "shimmer 1.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
