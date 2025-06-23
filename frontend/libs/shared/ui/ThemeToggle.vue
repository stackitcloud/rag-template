<script setup lang="ts">
import { useThemeStore } from "../store/theme.store";
import { computed } from "vue";
import { SunIcon, MoonIcon } from "@heroicons/vue/24/outline";

const themeStore = useThemeStore();

const isDarkMode = computed(() => themeStore.currentTheme === "dark");

const toggleTheme = () => {
  themeStore.setTheme(isDarkMode.value ? "light" : "dark");
};
</script>

<template>
  <button
    @click="toggleTheme"
    class="btn btn-circle btn-ghost hover:bg-white/20"
    :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <SunIcon v-if="!isDarkMode" class="h-5 w-5" />
    <MoonIcon v-else class="h-5 w-5" />
  </button>
</template>
