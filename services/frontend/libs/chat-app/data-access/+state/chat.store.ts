import { newUid } from "@shared/utils";
import { marked } from "marked";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  ChatDocumentModel,
  mapToChatDocuments,
} from "../../models/chat-document.model";
import { ChatMessageModel } from "../../models/chat-message.model";
import { ChatRequestModel, mapToChatRequestModel } from "../../models/chat-request.model";
import { InformationPiece } from "../../models/chat-response.model";
import { DocumentResponseModel } from "../../models/document-response.model";
import { ChatAPI } from "../chat.api";
import { settings } from "@shared/settings";

export const useChatStore = defineStore("chat", () => {
  const conversationId = ref();
  const chatHistory = ref<ChatMessageModel[]>([]);
  const chatDocuments = ref<ChatDocumentModel[]>([]);
  const isLoading = ref(false);
  const hasError = ref(false);

  // Get i18n instance lazily to ensure it's available
  const getInitialMessage = () => {
    const { t } = useI18n();
    try {
      return t("chat.initialMessage", { bot_name: settings.bot.name });
    } catch (error) {
      console.warn("i18n interpolation failed, using fallback", error);
      return `Hi 👋, I'm your AI Assistant ${settings.bot.name}, here to support you with any questions regarding the provided documents!`;
    }
  };
  const lastMessage = () => chatHistory.value[chatHistory.value.length - 1];

  function addHistory(prompt: string) {
    chatHistory.value.push({
      id: newUid(),
      text: prompt,
      role: "user",
    });

    chatHistory.value.push({
      id: newUid(),
      role: "assistant",
    });
  }

  function updateLatestMessage(update: Partial<ChatMessageModel>) {
    Object.assign(lastMessage(), update);
  }

  function prepareInferenceRequest(prompt: string): ChatRequestModel {
    const cleanedHistory = chatHistory.value.filter(
      (message: ChatMessageModel) => !message.skipAPI,
    );
    const requestMessages = mapToChatRequestModel(
      conversationId.value,
      prompt,
      cleanedHistory,
    );
    return requestMessages;
  }

  function parseDocumentsAsMarkdown(
    documents: InformationPiece[],
  ): Promise<DocumentResponseModel[]> {
    return Promise.all(
      documents.map(async (o) => {
        const chunk = await marked(o.page_content);
        return {
          ...o,
          page_content: chunk,
        } as DocumentResponseModel;
      }),
    );
  }

  const callInference = async (prompt: string) => {
    isLoading.value = true;
    try {
      const requestMessages = prepareInferenceRequest(prompt);

      const promptAsMd = await marked(prompt);
      addHistory(promptAsMd);

      const response = await ChatAPI.callInference(requestMessages);

      const textAsMd = await marked(response.answer);
      const documentsAsMd = await parseDocumentsAsMarkdown(response.citations);
      const documents = mapToChatDocuments(
        chatDocuments.value.length,
        documentsAsMd,
        lastMessage().id,
      );

      updateLatestMessage({
        dateTime: new Date(),
        text: textAsMd,
        anchorIds: documents.map((o) => o.index),
      });

      chatDocuments.value.push(...documents);
    } catch (error) {
      updateLatestMessage({
        hasError: true,
        dateTime: new Date(),
      });
    } finally {
      isLoading.value = false;
    }
  };

  const initiateConversation = (id: string) => {
    conversationId.value = id;
    chatHistory.value.push({
      id: newUid(),
      text: getInitialMessage(),
      role: "assistant",
      skipAPI: true,
    });
  };

  return {
    chatDocuments,
    chatHistory,
    isLoading,
    hasError,
    conversationId,
    callInference,
    initiateConversation,
  };
});