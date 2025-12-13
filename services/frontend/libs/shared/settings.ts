export interface AppSettings {
  bot: {
    name: string;
  };
  ui: {
    logoPath: string; // deprecated
    logo: {
      light: string;
      dark: string;
    };
    theme: {
      default: string;
      options: string[];
    };
  };
  features?: {
    useMockData?: boolean;
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
    logo: {
      light: "/assets/navigation-logo-light.svg",
      dark: "/assets/navigation-logo-dark.svg",
    },
    theme: {
      default: "dark",
      options: ["light", "dark"],
    },
  },
  features: {
    useMockData: false,
  },
};

// Helper getters that normalize empty strings and whitespace
const envStr = (val: unknown | undefined, fallback: string): string => {
  if (typeof val !== 'string') return fallback;
  const v = val.trim();
  return v.length > 0 ? v : fallback;
};

const envBool = (val: unknown | undefined, fallback: boolean): boolean => {
  if (typeof val !== 'string') return fallback;
  const v = val.trim().toLowerCase();
  if (v === 'true') return true;
  if (v === 'false') return false;
  return fallback;
};

// Load settings from environment variables with fallbacks to defaults
export const settings: AppSettings = {
  bot: {
    // Ensure a sensible default if VITE_BOT_NAME is missing or empty
    name: envStr(import.meta.env.VITE_BOT_NAME, defaultSettings.bot.name),
  },
  ui: {
    logoPath: envStr(import.meta.env.VITE_UI_LOGO_PATH, defaultSettings.ui.logoPath),
    logo: {
      // Support specific light/dark envs and fall back to common path or defaults
      light: envStr(
        import.meta.env.VITE_UI_LOGO_PATH_LIGHT,
        envStr(import.meta.env.VITE_UI_LOGO_PATH, defaultSettings.ui.logo.light)
      ),
      dark: envStr(
        import.meta.env.VITE_UI_LOGO_PATH_DARK,
        envStr(import.meta.env.VITE_UI_LOGO_PATH, defaultSettings.ui.logo.dark)
      ),
    },
    theme: {
      default: envStr(import.meta.env.VITE_UI_THEME_DEFAULT, defaultSettings.ui.theme.default),
      options:
        typeof import.meta.env.VITE_UI_THEME_OPTIONS === 'string' && import.meta.env.VITE_UI_THEME_OPTIONS.trim()
          ? import.meta.env.VITE_UI_THEME_OPTIONS.split(',').map((s) => s.trim()).filter(Boolean)
          : defaultSettings.ui.theme.options,
    },
  },
  features: {
    useMockData: envBool(import.meta.env.VITE_USE_MOCK_DATA, defaultSettings.features?.useMockData ?? false),
  },
};
