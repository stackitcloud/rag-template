export interface AppSettings {
  bot: {
    name: string;
  };
  ui: {
    logoPath: string;
    theme: {
      default: string;
      options: string[];
    };
  };
  // Add other configuration sections as needed
}

// Default settings to use as fallbacks
const defaultSettings: AppSettings = {
  bot: {
    name: "Knowledge Agent",
  },
  ui: {
    logoPath: "/assets/navigation-logo.svg",
    theme: {
      default: "dark",
      options: ["light", "dark"],
    },
  },
};

// Load settings from environment variables with fallbacks to defaults
export const settings: AppSettings = {
  bot: {
    name: import.meta.env.VITE_BOT_NAME || defaultSettings.bot.name,
  },
  ui: {
    logoPath: import.meta.env.VITE_UI_LOGO_PATH || defaultSettings.ui.logoPath,
    theme: {
      default:
        import.meta.env.VITE_UI_THEME_DEFAULT ||
        defaultSettings.ui.theme.default,
      options: import.meta.env.VITE_UI_THEME_OPTIONS
        ? (import.meta.env.VITE_UI_THEME_OPTIONS as string).split(",")
        : defaultSettings.ui.theme.options,
    },
  },
};
