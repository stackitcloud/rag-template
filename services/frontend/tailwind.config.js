/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "apps/**/index.html",
    "apps/**/src/**/*.{vue,js,ts}",
    "libs/**/*.{vue,js,ts}",
  ],
  theme: {
    extend: {
      typography: (theme) => ({
        dark: {
          css: {
            color: theme("colors.white"),
            "h1, h2, h3, h4": {
              color: theme("colors.white"),
            },
            a: {
              color: theme("colors.white"),
            },
            strong: {
              color: theme("colors.white"),
            },
            "ol > li::marker": {
              color: theme("colors.white"),
            },
            "ul > li::marker": {
              color: theme("colors.white"),
            },
            li: {
              color: theme("colors.white"),
            },
            blockquote: {
              color: theme("colors.white"),
            },
            code: {
              color: theme("colors.white"),
            },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          // Light color for primary (navigation) in light mode
          primary: "#f8f9fa",
          "primary-content": "#0a1e2d", // Dark text on light background

          // Secondary color
          secondary: "#ffffff", // Gray-80
          "secondary-content": "#575756",

          // Spacemint for accent buttons (btn-accent)
          accent: "#00c3cd", // Spacemint
          "accent-content": "#fff",

          // Neutral colors
          neutral: "#B2B2B2",
          "neutral-content": "#0a1e2d",

          // Base colors - WHITE BACKGROUND
          "base-100": "#ffffff", // White background
          "base-200": "#EDEDED", // Gray-10
          "base-300": "#DADADA", // Gray-20
          "base-content": "#333333", // Dark text for light theme

          // Info, success, warning, error
          info: "#00c3cd", // Spacemint
          success: "#00c387", // Fresh Green
          warning: "#fafc00", // Sunshine
          error: "#ff0555", // Coral

          // Scrollbar and highlights
          "--scrollbar-track": "#ffffff",
          "--scrollbar-thumb": "rgba(10, 30, 45, 0.3)",
          "--base-200-highlight": "#C6C6C6",

          // Fix for chat text color
          ".chat-text": "#333333", // Dark text color for chat in light mode
        },
        dark: {
          // Keep Navy Blue for primary (navigation) in dark mode
          primary: "#0a1e2d",
          "primary-content": "#ffffff",

          // Secondary color
          secondary: "#575756", // Gray-80
          "secondary-content": "#ffffff",

          // Spacemint for accent buttons (btn-accent)
          accent: "#00c3cd", // Spacemint
          "accent-content": "#fff",

          // Neutral colors
          neutral: "#B2B2B2",
          "neutral-content": "#ffffff",

          // Base colors - DARK BACKGROUND
          "base-100": "#1e1e1e", // Dark background
          "base-200": "#2d2d2d", // Dark Gray
          "base-300": "#3d3d3d", // Medium Gray
          "base-content": "#f5f5f5", // Light text for dark theme

          // Info, success, warning, error
          info: "#00c3cd", // Spacemint
          success: "#00c387", // Fresh Green
          warning: "#fafc00", // Sunshine
          error: "#ff0555", // Coral

          // Scrollbar and highlights
          "--scrollbar-track": "#2d2d2d",
          "--scrollbar-thumb": "rgba(255, 255, 255, 0.3)",
          "--base-200-highlight": "#4d4d4d",

          // Fix for chat text color
          ".chat-text": "#f5f5f5", // Light text color for chat in dark mode
        },
      },
    ],
    utils: true,
    logs: false,
    themeRoot: ":root",
  },
};
