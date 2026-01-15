import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { settings } from "../settings";

export const useThemeStore = defineStore("theme", () => {
  const THEME_STORAGE_KEY = "app-theme";
  type Theme = string;

  const availableThemes: Theme[] = (Array.isArray(settings.ui.theme.options) ? settings.ui.theme.options : [])
    .map((t) => (typeof t === "string" ? t.trim() : ""))
    .filter(Boolean);

  const defaultTheme: Theme =
    availableThemes.includes(settings.ui.theme.default) && settings.ui.theme.default.trim()
      ? settings.ui.theme.default
      : availableThemes[0] ?? settings.ui.theme.default ?? "dark";

  const currentTheme = ref<Theme>(loadSavedTheme());

  function isValidTheme(theme: string): theme is Theme {
    return availableThemes.includes(theme);
  }

  function loadSavedTheme(): Theme {
    try {
      const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      return savedTheme && isValidTheme(savedTheme) ? savedTheme : defaultTheme;
    } catch {
      return defaultTheme;
    }
  }

  function setTheme(theme: string) {
    if (!isValidTheme(theme)) return;
    currentTheme.value = theme;
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // ignore
    }
    applyTheme(theme);
  }

  function applyTheme(theme: string) {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.classList.remove(...availableThemes);
    document.documentElement.classList.add(theme);
  }

  // Initialize theme
  applyTheme(currentTheme.value);

  // Computed property for dark mode check
  const isDarkMode = computed(() => currentTheme.value === "dark");

  return { currentTheme, setTheme, availableThemes, isDarkMode };
});
