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
    name: "Knowledge Agent",
  },
  ui: {
    logoPath: "/assets/navigation-logo.svg",
    theme: {
      default: "light",
      options: ["light", "dark"],
    },
  },
};
