<script lang="ts" setup>
import { ChatBubbleModel } from "../models/chat-bubble.model";
import { iconCheck, iconCopy, iconFile } from "@sit-onyx/icons";
import { OnyxIcon } from "@shared/ui";
import { nextTick, ref } from "vue";
import { useChatStore } from "../data-access/+state/chat.store";
import { COPY_FEEDBACK_DURATION_MS, copyToClipboard } from "@shared/utils";

const props = defineProps<ChatBubbleModel>();
const chatStore = useChatStore();
const messageRef = ref<HTMLElement>();
const isCopied = ref(false);
let copyTimeoutId: number | undefined;

const copyMessage = async () => {
  const text = props.rawText ?? messageRef.value?.innerText ?? "";
  if (!text.trim()) return;

  const ok = await copyToClipboard(text);
  if (!ok) return;

  isCopied.value = true;
  if (copyTimeoutId) window.clearTimeout(copyTimeoutId);
  copyTimeoutId = window.setTimeout(() => {
    isCopied.value = false;
    copyTimeoutId = undefined;
  }, COPY_FEEDBACK_DURATION_MS);
		};

const scrollReveal = (anchorId: string) => {
  const item = document.getElementById(anchorId);
  if (item) {
    item.classList.add("base-200-highlight");
    item.scrollIntoView({ behavior: "smooth", block: "start" });

    setTimeout(() => {
      item?.classList?.remove("base-200-highlight");
    }, 3000);
  }
};

const revealSource = async (anchorId: string) => {
  if (!chatStore.isSourcesPanelOpen) {
    chatStore.openSourcesPanel();
    await nextTick();
  }

  scrollReveal(anchorId);
};
</script>

<template>
  <div
    :class="[
      'chat overflow-hidden',
      {
        'chat-start slide-in-left': props.align === 'left',
        'chat-end slide-in-right': props.align === 'right',
      },
    ]"
  >
    <div class="chat-image avatar">
      <div class="w-10 rounded-full">
        <img class="ai-avatar" :src="props.avatarSrc" />
      </div>
    </div>
    <div class="chat-header">
      {{ props.name }}
      <time class="text-xs opacity-50">{{ props.time }}</time>
    </div>
    <div
      class="chat-bubble"
      :id="props.id"
      :class="[props.backgroundColor, props.textColor]"
    >
      <div v-if="props.text !== undefined" class="flex flex-col">
        <article
          ref="messageRef"
          :class="[
            'flex-1',
            'text-pretty',
            'break-words',
            'prose',
            'prose-sm',
            'max-w-none',
            'chat-text',
            props.proseDark,
          ]"
          v-html="props.text"
        ></article>

        <div class="flex items-start gap-2 mt-2">
          <!-- Document jump anchors-->
          <div
            v-if="props.anchorIds !== undefined"
            class="flex flex-wrap gap-3 text-secondary-content text-sm cursor-pointer flex-1 min-w-0"
          >
            <div
              class="flex items-center"
              v-for="anchorId in anchorIds"
              :key="anchorId"
              @click="revealSource(anchorId.toString())"
            >
              <OnyxIcon :icon="iconFile" :size="16" class="mr-1" />
              {{ anchorId }}
            </div>
          </div>
          <div v-else class="flex-1"></div>

          <button
            type="button"
            class="chat-bubble-copy-button shrink-0"
            :title="isCopied ? 'Copied!' : 'Copy to clipboard'"
            :aria-label="isCopied ? 'Copied' : 'Copy message to clipboard'"
            @click="copyMessage"
          >
            <OnyxIcon :icon="isCopied ? iconCheck : iconCopy" :size="16" />
          </button>
        </div>
      </div>
      <span v-else class="jumping-dots text-lg">
        <span class="dot-1">.</span>
        <span class="dot-2">.</span>
        <span class="dot-3">.</span>
      </span>
    </div>
  </div>
</template>

<style scoped lang="css">
.chat-text > * {
  overflow-wrap: anywhere;
  word-break: normal;
}

.chat-text pre {
  white-space: pre;
  word-break: normal;
  overflow-wrap: normal;
}

.jumping-dots span {
  position: relative;
  bottom: 0px;
  animation: jump 1s infinite;
}

.jumping-dots .dot-1 {
  animation-delay: 100ms;
}

.jumping-dots .dot-2 {
  animation-delay: 200ms;
}

.jumping-dots .dot-3 {
  animation-delay: 400ms;
}

@keyframes jump {
  0% {
    bottom: 0px;
  }

  20% {
    bottom: 5px;
  }

  40% {
    bottom: 0px;
  }
}

.slide-in-right {
  animation: slide-in-right 0.5s both;
}

@keyframes slide-in-right {
  0% {
    transform: translateX(30px);
    opacity: 0;
  }

  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in-left {
  animation: slide-in-left 0.5s both;
}

@keyframes slide-in-left {
  0% {
    transform: translateX(-30px);
    opacity: 0;
  }

  100% {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
