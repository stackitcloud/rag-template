// frontend/libs/shared/ui/NavigationContainer.vue

<script lang="ts" setup>
import { settings } from "../settings";
import { useThemeStore } from "../store/theme.store";
import ThemeToggle from "./ThemeToggle.vue";

// Use the logo path from settings
const logoPath = settings.ui.logoPath;
const themeStore = useThemeStore();
</script>

<template>
  <div class="bg-primary flex p-4">
    <div class="flex-1">
      <img :src="logoPath" class="w-32" />
    </div>
    <div class="flex items-center gap-2">
      <ThemeToggle />
      <slot></slot>
    </div>
  </div>
</template>
