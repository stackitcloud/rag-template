<script lang="ts" setup>
import ChatInput from "./ChatInput.vue";
import ChatMessages from "../ui/ChatMessages.vue";
import ChatDisclaimer from "./ChatDisclaimer.vue";
import { useChatStore } from "../data-access/+state/chat.store";
import ChatDocumentContainer from "../ui/ChatDocumentContainer.vue";
import { onMounted } from "vue";
import { newUid } from "@shared/utils";
import { iconChevronLeft, iconChevronRight } from "@sit-onyx/icons";
import { OnyxIcon } from "@shared/ui";

const chatStore = useChatStore();

onMounted(() => chatStore.initiateConversation(newUid()));
</script>

<template>
  <div
    data-testid="chat-view"
    class="md:container md:mx-auto h-full p-4 flex gap-0"
  >
    <div class="flex-1 min-w-0 flex flex-col overflow-hidden">
      <div class="flex-1 mb-4 overflow-hidden">
        <ChatMessages
          :messages="chatStore.chatHistory"
          :is-loading="chatStore.isLoading"
        />
      </div>
      <ChatInput :is-disabled="chatStore.isLoading" />
      <ChatDisclaimer class="mt-2 mx-1" />
    </div>

    <!-- Divider / fold handle -->
    <div class="sources-divider">
      <button
        type="button"
        class="sources-divider__button"
        :aria-label="chatStore.isSourcesPanelOpen ? 'Hide sources' : 'Show sources'"
        :title="chatStore.isSourcesPanelOpen ? 'Hide sources' : 'Show sources'"
        @click="chatStore.toggleSourcesPanel"
      >
        <OnyxIcon :icon="chatStore.isSourcesPanelOpen ? iconChevronRight : iconChevronLeft" :size="18" />
      </button>
    </div>

    <div
      class="flex-none overflow-hidden transition-all duration-200"
      :class="chatStore.isSourcesPanelOpen ? 'w-72 md:w-4/12' : 'w-0'"
    >
      <div v-show="chatStore.isSourcesPanelOpen" class="h-full">
        <ChatDocumentContainer :documents="chatStore.chatDocuments" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.sources-divider {
  position: relative;
  flex: none;
  width: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.sources-divider::before {
  content: "";
  position: absolute;
  inset: 0;
  left: 50%;
  width: 1px;
  transform: translateX(-0.5px);
  background: var(--fallback-b3, oklch(var(--b3) / 1));
}

.sources-divider__button {
  position: relative;
  z-index: 10;
  width: 1.75rem;
  height: 1.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  border: 1px solid var(--fallback-b3, oklch(var(--b3) / 1));
  background: var(--fallback-b1, oklch(var(--b1) / 1));
  color: var(--fallback-bc, oklch(var(--bc) / 0.7));
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  transition:
    background-color 150ms ease,
    color 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease,
    transform 120ms ease;
}

.sources-divider__button:hover {
  background: var(--fallback-b2, oklch(var(--b2) / 1));
  color: var(--fallback-bc, oklch(var(--bc) / 0.85));
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.14);
}

.sources-divider__button:active {
  transform: scale(0.96);
}

.sources-divider__button:focus-visible {
  outline: 2px solid var(--fallback-in, oklch(var(--in) / 1));
  outline-offset: 2px;
}
</style>
