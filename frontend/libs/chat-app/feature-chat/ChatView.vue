<script lang="ts" setup>
import ChatInput from './ChatInput.vue'
import ChatMessages from '../ui/ChatMessages.vue'
import {useChatStore} from '../data-access/+state/chat.store';
import ChatDocumentContainer from '../ui/ChatDocumentContainer.vue';
import {onMounted} from "vue";
import {newUid} from "@shared/utils";

const chatStore = useChatStore();

onMounted(() => chatStore.initiateConversation(newUid()));
</script>

<template>
    <div data-testid="chat-view" class="md:container md:mx-auto h-full p-4 flex gap-4">
        <div class="flex-1 flex flex-col">
            <div class="flex-1 mb-4 overflow-hidden">
                <ChatMessages :messages="chatStore.chatHistory" :is-loading="chatStore.isLoading" />
            </div>
            <ChatInput :is-disabled="chatStore.isLoading" />
        </div>
        <div class="w-full md:w-4/12">
            <ChatDocumentContainer :documents="chatStore.chatDocuments"></ChatDocumentContainer>
        </div>
    </div>
</template>