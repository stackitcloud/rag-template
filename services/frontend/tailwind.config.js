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
        DEFAULT: {
          css: {
            color: "hsl(var(--bc) / 1)",
            "h1, h2, h3, h4": {
              color: "hsl(var(--bc) / 1)",
            },
            a: {
              color: "hsl(var(--in) / 1)",
            },
            strong: {
              color: "hsl(var(--bc) / 1)",
            },
            "ol > li::marker": {
              color: "hsl(var(--bc) / 0.8)",
            },
            "ul > li::marker": {
              color: "hsl(var(--bc) / 0.8)",
            },
            li: {
              color: "hsl(var(--bc) / 1)",
            },
            blockquote: {
              color: "hsl(var(--bc) / 1)",
            },
            code: {
              color: "hsl(var(--bc) / 1)",
            },
          },
        },
        dark: {
          css: {
            color: "hsl(var(--bc) / 1)",
            "h1, h2, h3, h4": {
              color: "hsl(var(--bc) / 1)",
            },
            a: {
              color: "hsl(var(--in) / 1)",
            },
            strong: {
              color: "hsl(var(--bc) / 1)",
            },
            "ol > li::marker": {
              color: "hsl(var(--bc) / 0.8)",
            },
            "ul > li::marker": {
              color: "hsl(var(--bc) / 0.8)",
            },
            li: {
              color: "hsl(var(--bc) / 1)",
            },
            blockquote: {
              color: "hsl(var(--bc) / 1)",
            },
            code: {
              color: "hsl(var(--bc) / 1)",
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
          // Matches STACKIT docs (digits light)
          primary: "#00c3cd",
          "primary-content": "#091a26",

          secondary: "#ccf3f5",
          "secondary-content": "#162938",

          accent: "#00c3cd",
          "accent-content": "#091a26",

          neutral: "#162938",
          "neutral-content": "#f8f9fa",

          "base-100": "#ffffff",
          "base-200": "#f0f2f4",
          "base-300": "#e7eaed",
          "base-content": "#162938",

          info: "#127481",
          "info-content": "#f8f9fa",

          success: "#45a85d",
          "success-content": "#091a26",

          warning: "#e3774c",
          "warning-content": "#091a26",

          error: "#dc1f1f",
          "error-content": "#f8f9fa",

          "--scrollbar-track": "#ffffff",
          "--scrollbar-thumb": "rgba(22, 41, 56, 0.35)",
          "--base-200-highlight": "#ccf3f5",
        },
        dark: {
          // Matches STACKIT docs (digits dark)
          primary: "#00c3cd",
          "primary-content": "#091a26",

          secondary: "#165e6c",
          "secondary-content": "#e7eaed",

          accent: "#00c3cd",
          "accent-content": "#091a26",

          neutral: "#162938",
          "neutral-content": "#e7eaed",

          "base-100": "#091a26",
          "base-200": "#233542",
          "base-300": "#2c3d4a",
          "base-content": "#e7eaed",

          info: "#66dbe1",
          "info-content": "#091a26",

          success: "#51cf66",
          "success-content": "#091a26",

          warning: "#e3774c",
          "warning-content": "#091a26",

          error: "#e34c4c",
          "error-content": "#091a26",

          "--scrollbar-track": "#091a26",
          "--scrollbar-thumb": "rgba(231, 234, 237, 0.25)",
          "--base-200-highlight": "#165e6c",
        },
      },
    ],
    utils: true,
    logs: false,
    themeRoot: ":root",
  },
};
