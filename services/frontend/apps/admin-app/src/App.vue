<script lang="ts" setup>
import { NavigationContainer, OnyxIcon } from "@shared/ui";
import { iconArrowSmallUpRightTop } from "@sit-onyx/icons";
import { useI18n } from "vue-i18n";
import { RouterView } from "vue-router";

const { t } = useI18n();
const chatURL = import.meta.env.VITE_CHAT_URL;
</script>

<template>
  <main class="bg-base-100 flex flex-col overflow-hidden">
    <NavigationContainer>
      <a
        class="flex gap-2 items-center btn btn-primary btn-sm"
        target="_blank"
        :href="chatURL"
      >
        <OnyxIcon :icon="iconArrowSmallUpRightTop" :size="16" />
        {{ t("documents.chat") }}
      </a>
    </NavigationContainer>
    <RouterView class="flex-1" />
  </main>
</template>

<style lang="css">
@import "@shared/style";
</style>
