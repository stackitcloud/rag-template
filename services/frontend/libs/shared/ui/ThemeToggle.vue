<script setup lang="ts">
import { useThemeStore } from "../store/theme.store";
import { computed } from "vue";
import { iconMoon, iconSunny } from "@sit-onyx/icons";
import OnyxIcon from "./OnyxIcon.vue";

const themeStore = useThemeStore();

const isDarkMode = computed(() => themeStore.currentTheme === "dark");
const canToggle = computed(
  () =>
    themeStore.availableThemes.includes("light") &&
    themeStore.availableThemes.includes("dark") &&
    themeStore.availableThemes.length > 1,
);

const toggleTheme = () => {
  themeStore.setTheme(isDarkMode.value ? "light" : "dark");
};
</script>

<template>
  <button
    v-if="canToggle"
    @click="toggleTheme"
    class="btn btn-circle btn-ghost hover:bg-base-200"
    :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <OnyxIcon v-if="!isDarkMode" :icon="iconSunny" :size="20" />
    <OnyxIcon v-else :icon="iconMoon" :size="20" />
  </button>
</template>
