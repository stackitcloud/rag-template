import { defineStore } from "pinia";
import { ref, watch, computed } from "vue";
import { settings } from "../settings";

export const useThemeStore = defineStore("theme", () => {
  const THEME_STORAGE_KEY = "app-theme";
  type Theme = "light" | "dark" | "system"; // Define allowed theme values
  const availableThemes: Theme[] = settings.ui.theme.options as Theme[];
  const currentTheme = ref(loadSavedTheme());

  function isValidTheme(theme: string): theme is Theme {
    return availableThemes.includes(theme as Theme);
  }

  function loadSavedTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    return savedTheme && isValidTheme(savedTheme)
      ? savedTheme
      : settings.ui.theme.default;
  }

  function setTheme(theme: string) {
    if (!isValidTheme(theme)) return;
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

  // Computed property for dark mode check
  const isDarkMode = computed(() => currentTheme.value === "dark");

  return { currentTheme, setTheme, availableThemes, isDarkMode };
});
