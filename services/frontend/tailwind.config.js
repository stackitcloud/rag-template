/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "apps/**/index.html",
    "apps/**/src/**/*.{vue,js,ts}",
    "libs/**/*.{vue,js,ts}"
  ],
  theme: {
    extend: {
      typography: (theme) => ({
        dark: {
          css: {
            color: theme('colors.white'),
            'h1, h2, h3, h4': {
              color: theme('colors.white'),
            },
            a: {
              color: theme('colors.white'),
            },
            strong: {
              color: theme('colors.white'),
            },
            'ol > li::marker': {
              color: theme('colors.white'),
            },
            'ul > li::marker': {
              color: theme('colors.white'),
            },
            li: {
              color: theme('colors.white'), // For list items themselves
            },
            blockquote: {
              color: theme('colors.white'),
            },
            code: {
              color: theme('colors.white'),
            },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography'), require("daisyui")],
  daisyui: {
    themes: [
      {
        appTheme: {
          "secondary": "#f6d860",
          "primary": "#045462",
          "primary-content": "#ffff",

          "accent": "#F8EC17",
          "accent-content": "#045462",

          "neutral": "#334155",
          "neutral-content": "#F1F5F9",

          "base-100": "#ffffff",
          "base-200": "#F9FAFB",
          "base-300": "#D1D5DB",

          "info": "#41AEF5",

          '--scrollbar-track': '#ffff',
          '--scrollbar-thumb': 'rgba(0, 0, 0, .3)',
          "--base-200-highlight": "#E5EDEF",
        }
      }
    ],
    utils: true,
    logs: false,
    themeRoot: "#app",
  }
}
