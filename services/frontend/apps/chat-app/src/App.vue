<script lang="ts" setup>
import { ArrowTopRightOnSquareIcon } from "@heroicons/vue/24/outline";
import { NavigationContainer } from "@shared/ui";
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView } from "vue-router";

const { t } = useI18n();
const adminURL = import.meta.env.VITE_ADMIN_URL;

import { useThemeStore } from "@shared/store/theme.store";
import { onMounted } from "vue";
onMounted(() => {
  // Initialize theme
  const themeStore = useThemeStore();
});
</script>

<template>
  <main class="bg-base-100 flex flex-col">
    <NavigationContainer>
      <RouterLink
        class="btn btn-outline btn-sm"
        :to="{ name: 'portal-home' }"
      >
        {{ t("chat.backToSearch") }}
      </RouterLink>
      <a
        class="flex gap-2 items-center btn btn-primary border border-opacity-10 border-white btn-sm"
        target="_blank"
        :href="adminURL"
      >
        <ArrowTopRightOnSquareIcon class="w-4 h-4" />
        {{ t("chat.documents") }}
      </a>
    </NavigationContainer>
    <RouterView class="flex-1 overflow-hidden" />
  </main>
</template>

<style lang="css">
@import "@shared/style";
</style>
