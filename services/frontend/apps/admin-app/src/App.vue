<script lang="ts" setup>
import { RouterView } from "vue-router";
import { LogoContainer, NavigationContainer } from "@shared/ui";
import { useI18n } from "vue-i18n";
import { ArrowTopRightOnSquareIcon } from "@heroicons/vue/24/outline";

const { t } = useI18n();
const chatURL = import.meta.env.VITE_CHAT_URL;
</script>

<template>
  <main class="bg-base-100 flex flex-col overflow-hidden">
    <NavigationContainer>
      <a
        class="flex gap-2 items-center btn btn-primary border border-opacity-10 border-white btn-sm"
        target="_blank"
        :href="chatURL"
      >
        <ArrowTopRightOnSquareIcon class="w-4 h-4" />
        {{ t("documents.chat") }}
      </a>
    </NavigationContainer>
    <RouterView class="flex-1" />
  </main>
</template>

<style lang="css">
@import "@shared/style";
</style>
