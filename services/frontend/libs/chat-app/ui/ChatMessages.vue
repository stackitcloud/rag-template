<script lang="ts" setup>
import { settings } from "@shared/settings";
import { extractTime } from "@shared/utils";
import { computed, nextTick, onUpdated, ref } from "vue";
import { useI18n } from "vue-i18n";
import { ChatBubbleModel } from "../models/chat-bubble.model";
import { ChatMessageModel } from "../models/chat-message.model";
import ChatBubble from "./ChatBubble.vue";
const USER_AVATAR = "/assets/user.svg?v=2";
const AI_AVATAR = "/assets/ai-avatar.svg";

const chatContainer = ref<HTMLElement>();
const { t } = useI18n();

const props = defineProps<{
  messages: Array<ChatMessageModel>;
}>();

const mapToChatBubble = (message: ChatMessageModel): ChatBubbleModel => {
  const isHuman = message.role === "user";
  const backgroundColor = isHuman ? "bg-base-200" : "bg-secondary";
  const textColor = isHuman ? "text-base-content" : "text-secondary-content";
  const proseDark = "";
  const avatarSrc = isHuman ? USER_AVATAR : AI_AVATAR;
  const align = isHuman ? "right" : "left";
  const time = message.dateTime ? extractTime(message.dateTime) : undefined;
  const name = isHuman ? "" : settings.bot.name;
  const anchorIds = isHuman ? undefined : message.anchorIds;

  const mapped: ChatBubbleModel = {
    id: message.id,
    text: message.text,
    rawText: message.rawText,
    name,
    backgroundColor,
    anchorIds,
    textColor,
    proseDark,
    avatarSrc,
    align,
    time,
  };

  if (message.hasError) {
    mapped.text = t("chat.error.requestError");
    mapped.rawText = mapped.text;
    mapped.textColor = "text-error";
  }

  return mapped;
};

const messages = computed((): ChatBubbleModel[] => {
  return props.messages.map((message: ChatMessageModel) =>
    mapToChatBubble(message),
  );
});

onUpdated(async () => {
  await nextTick();
  chatContainer!.value!.scrollTo({
    top: chatContainer!.value!.scrollHeight,
    behavior: "smooth",
  });
});
</script>
<template>
  <div class="h-full bg-base-100 rounded-box p-2">
    <div
      class="overflow-y-auto overflow-x-hidden h-full p-2 md:p-4 overscroll-contain"
      ref="chatContainer"
    >
      <ChatBubble
        v-for="message in messages"
        class="mb-2"
        :key="message.id"
        :id="message.id"
        :text="message.text"
        :rawText="message.rawText"
        :time="message.time"
        :avatarSrc="message.avatarSrc"
        :name="message.name"
        :align="message.align"
        :backgroundColor="message.backgroundColor"
        :textColor="message.textColor"
        :proseDark="message.proseDark"
        :anchorIds="message.anchorIds"
      />
    </div>
  </div>
</template>
