// frontend/libs/shared/ui/NavigationContainer.vue

<script lang="ts" setup>
import { computed } from "vue";
import { settings } from "../settings";
import { useThemeStore } from "../store/theme.store";
import ThemeToggle from "./ThemeToggle.vue";

const themeStore = useThemeStore();
const logoSrc = computed(() =>
  themeStore.isDarkMode ? settings.ui.logo.dark : settings.ui.logo.light
);
</script>

<template>
  <div class="bg-primary flex p-4">
    <div class="flex-1">
      <img :src="logoSrc" class="w-32" />
    </div>
    <div class="flex items-center gap-2">
      <ThemeToggle />
      <slot></slot>
    </div>
  </div>
</template>
