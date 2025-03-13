import { newUid } from "@shared/utils";
import { InformationPiece } from "libs/chat-app/models/chat-response.model";
import { DocumentResponseModel } from "libs/chat-app/models/document-response.model";
import { marked } from "marked";
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ChatDocumentModel, mapToChatDocuments } from "../../models/chat-document.model";
import { ChatMessageModel } from "../../models/chat-message.model";
import { ChatRequestModel, mapToChatRequestModel } from "../../models/chat-request.model";
import { ChatAPI } from "../chat.api";

export const useChatStore = defineStore('chat', () => {
    const {t, locale} = useI18n();
    const conversationId = ref();
    const chatHistory = ref<ChatMessageModel[]>([]);
    const chatDocuments = ref<ChatDocumentModel[]>([]);
    const isLoading = ref(false);
    const hasError = ref(false);
    const initialMessage = computed(() => t('chat.initialMessage'));
    const lastMessage = () => chatHistory.value[chatHistory.value.length - 1];

    function addHistory(prompt: string) {
        chatHistory.value.push({
            id: newUid(),
            text: prompt,
            role: 'user'
        });

        chatHistory.value.push({
            id: newUid(),
            role: 'assistant'
        });
    }

    function updateLatestMessage(update: Partial<ChatMessageModel>) {
        Object.assign(lastMessage(), update);
    }

    function prepareInferenceRequest(prompt: string): ChatRequestModel {
        const cleanedHistory = chatHistory.value.filter((message: ChatMessageModel) => !message.skipAPI)
        const requestMessages = mapToChatRequestModel(
            conversationId.value,
            prompt,
            cleanedHistory
        );
        return requestMessages;
    }

    function parseDocumentsAsMarkdown(documents: InformationPiece[]): Promise<DocumentResponseModel[]> {
        return Promise.all(documents.map(async o => {
            let a = JSON.parse(o);
            const chunk = await marked(a.page_content);
            return {
                ...a,
                page_content: chunk,
            } as DocumentResponseModel;
        }));
    }

    const callInference = async (prompt: string) => {
        isLoading.value = true;
        try {
            const requestMessages = prepareInferenceRequest(prompt);

            const promptAsMd = await marked(prompt)
            addHistory(promptAsMd);

            const stream = await ChatAPI.callInference(requestMessages);

            
            let fullchunk = {};
            for await (const chunk of stream) {
                console.log(chunk)
                fullchunk = {
                    ...JSON.parse(chunk),
                    ...fullchunk
                  };
                console.log(fullchunk)
                let abc=fullchunk;
                let documentsAsMd = await parseDocumentsAsMarkdown( abc?.citations|| "...");
                console.log("parse");
                let documents = mapToChatDocuments(chatDocuments.value.length, documentsAsMd, lastMessage().id);
                chatDocuments.value.push(...documents);
                let textAsMd = await marked( fullchunk?.answer || "...");
                updateLatestMessage({
                    dateTime: new Date(),
                    text: textAsMd,
                    anchorIds: documents.map((o) => o.index)
                });

              }

        } catch(error) {
            updateLatestMessage({
                hasError: true,
                dateTime: new Date()
            });
        } finally {
            isLoading.value = false;
        }
    };

    const initiateConversation = (id: string) => {
        conversationId.value = id;
        chatHistory.value.push({
            id: newUid(),
            text: initialMessage,
            role: 'assistant',
            skipAPI: true
        });
    }

    return {chatDocuments, chatHistory, isLoading, hasError, conversationId, callInference, initiateConversation};
});
