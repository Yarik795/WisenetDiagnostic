/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "var(--bg-base)",
        surface: "var(--bg-surface)",
        elevated: "var(--bg-elevated)",
        border: "var(--border-subtle)",
        primary: "var(--text-primary)",
        secondary: "var(--text-secondary)",
        muted: "var(--text-muted)",
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
        },
        status: {
          ok: "var(--status-ok)",
          warn: "var(--status-warn)",
          error: "var(--status-error)",
          unknown: "var(--status-unknown)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "IBM Plex Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "8px",
      },
      maxWidth: {
        content: "1440px",
      },
    },
  },
  plugins: [],
};
