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

// Default settings that can be overridden
export const settings: AppSettings = {
  bot: {
    name: "Karl Kalle",
  },
  ui: {
    logoPath:
      "https://www.what-the-hack.saarland/sites/default/files/Logo-SAAR-HACKATHON-x2.jpg",
    theme: {
      default: "dark",
      options: ["light", "dark"],
    },
  },
};
