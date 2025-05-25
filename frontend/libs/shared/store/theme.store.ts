import { defineStore } from "pinia";
import { ref, watch } from "vue";
import { settings } from "../settings";

export const useThemeStore = defineStore("theme", () => {
  const THEME_STORAGE_KEY = "app-theme";
  const availableThemes = settings.ui.theme.options;
  const currentTheme = ref(loadSavedTheme());

  function loadSavedTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    return savedTheme && availableThemes.includes(savedTheme)
      ? savedTheme
      : settings.ui.theme.default;
  }

  function setTheme(theme: string) {
    if (!availableThemes.includes(theme)) return;
    currentTheme.value = theme;
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    applyTheme(theme);
  }

  function applyTheme(theme: string) {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.classList.remove(...availableThemes);
    document.documentElement.classList.add(theme);
  }

  // Initialize theme
  applyTheme(currentTheme.value);

  return { currentTheme, setTheme, availableThemes };
});
