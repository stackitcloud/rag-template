import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ChatAPI } from "../chat.api";
import { ChatMessageModel } from "../../models/chat-message.model";
import { ChatRequestModel, mapToChatRequestModel } from "../../models/chat-request.model";
import { marked } from "marked";
import { newUid } from "@shared/utils";
import { ChatDocumentModel, mapToChatDocuments } from "../../models/chat-document.model";
import { DocumentResponseModel } from "libs/chat-app/models/document-response.model";
import { SourceDocument } from "libs/chat-app/models/chat-response.model";

export const useChatStore = defineStore('chat', () => {
    const conversationId = ref();
    const chatHistory = ref<ChatMessageModel[]>([]);
    const chatDocuments = ref<ChatDocumentModel[]>([]);
    const isLoading = ref(false);
    const hasError = ref(false);
    //TODO Add an enviroment variable for the initial message and use the current one as default
    const initialMessage = "Hi👋 \n\nIch bin rag und Du kannst mir Fragen zum Inhalt von PDFs stellen.\n\nDokumente werden DSGVO-konform auf der STACKIT Cloud verarbeitet.\n\nStell mir doch einfach eine Frage zu einem der hochgeladenen Dokumente!\n\nHier etwas Inspiration:\n\nWie muss ich R3G500PA2803 anschließen?\n\nWie hoch ist die Stromaufnahme von R3G500PA2803?";
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

    function parseDocumentsAsMarkdown(documents: SourceDocument[]): Promise<DocumentResponseModel[]> {
        return Promise.all(documents.map(async o => {
            const chunk = await marked(o.content);
            return {
              chunk, // TODO keyto name
              ...o
            } as DocumentResponseModel;
        }));
    }

    const callInference = async (prompt: string) => {
        isLoading.value = true;
        try {
            const requestMessages = prepareInferenceRequest(prompt);
            console.log(requestMessages);
            addHistory(prompt);

            const response = await ChatAPI.callInference(requestMessages);

            const textAsMd = await marked(response.answer);
            const documentsAsMd = await parseDocumentsAsMarkdown(response.citations);
            const documents = mapToChatDocuments(chatDocuments.value.length, documentsAsMd, lastMessage().id);

            updateLatestMessage({
                dateTime: new Date(),
                text: textAsMd,
                anchorIds: documents.map((o) => o.index)
            });

            chatDocuments.value.push(...documents);

        } catch (error) {
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

    return { chatDocuments, chatHistory, isLoading, hasError, conversationId, callInference, initiateConversation };
});
