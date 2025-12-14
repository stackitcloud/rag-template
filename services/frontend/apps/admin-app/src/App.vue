<script lang="ts" setup>
import { RouterView } from "vue-router";
import { LogoContainer, NavigationContainer, OnyxIcon } from "@shared/ui";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { iconArrowSmallUpRightTop } from "@sit-onyx/icons";

const { t } = useI18n();
const isPlaceholderEnvValue = (value: unknown): boolean =>
  typeof value === "string" && /^VITE_[A-Z0-9_]+$/.test(value.trim());

const inferChatURLFromLocation = (): string => {
  if (typeof window === "undefined") return "/";

  const { protocol, hostname, port } = window.location;

  if (hostname === "localhost" && port === "4300") {
    return `${protocol}//${hostname}:4200`;
  }

  const inferredHostname = hostname.startsWith("admin.")
    ? hostname.slice("admin.".length)
    : hostname;

  const inferredPort = port ? `:${port}` : "";
  return `${protocol}//${inferredHostname}${inferredPort}`;
};

const chatURL = computed(() => {
  const configuredChatURL = import.meta.env.VITE_CHAT_URL;
  if (!configuredChatURL || isPlaceholderEnvValue(configuredChatURL)) {
    return inferChatURLFromLocation();
  }

  return String(configuredChatURL).trim();
});
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
