<script lang="ts" setup>
import { RouterView } from "vue-router";
import { NavigationContainer, OnyxIcon } from "@shared/ui";
import { useI18n } from "vue-i18n";
import { iconArrowSmallUpRightTop } from "@sit-onyx/icons";

const { t } = useI18n();
const adminURL = import.meta.env.VITE_ADMIN_URL;

import { onMounted } from "vue";
import { useThemeStore } from "@shared/store/theme.store";
onMounted(() => {
  // Initialize theme
  const themeStore = useThemeStore();
});
</script>

<template>
  <main class="bg-base-100 flex flex-col">
    <NavigationContainer>
      <a
        class="flex gap-2 items-center btn btn-primary btn-sm"
        target="_blank"
        :href="adminURL"
      >
        <OnyxIcon :icon="iconArrowSmallUpRightTop" :size="16" />
        {{ t("chat.documents") }}
      </a>
    </NavigationContainer>
    <RouterView class="flex-1 overflow-hidden" />
  </main>
</template>

<style lang="css">
@import "@shared/style";
</style>
