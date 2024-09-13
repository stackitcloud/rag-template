<script lang="ts" setup>
import ChatDocumentItem from './ChatDocumentItem.vue';
import ChatDocumentGroup from './ChatDocumentGroup.vue';
import { computed } from "vue";
import { useI18n } from 'vue-i18n';
import { isNotEmpty } from '@shared/utils';
import { ChatDocumentItemModel } from '../models/chat-document-item.model';
import { SideBarContainer } from '@shared/ui';
import { ChatDocumentModel } from '../models/chat-document.model';

const { t } = useI18n()

const props = defineProps<{
    documents: Array<ChatDocumentModel>
}>()

const mapToDocumentItem = (document: ChatDocumentModel): ChatDocumentItemModel => ({
    index: document.index,
    source: document.url,
    text: document.chunk,
    title: document.name,
    anchorId: document.messageId
});

const groupedDocuments = computed((): ChatDocumentItemModel[] => {
    const documents = props.documents.map((message) => mapToDocumentItem(message));
    const grouped = documents.reduce(
        (reduced: any, element: ChatDocumentItemModel) => {
            reduced[element.title] = reduced[element.title] || [];
            reduced[element.title].push(element);
            return reduced;
        }, Object.create(null));
    return grouped;
});
</script>
<template>
    <SideBarContainer :header="t('chat.sources')">
        <div v-if="isNotEmpty(groupedDocuments)">
            <ChatDocumentGroup v-for="(documents, title, index) in groupedDocuments" :key="index"
                :title="title" :source="documents[0].source">
                <ChatDocumentItem v-for="document in documents" :key="document.index" :id="document.index"
                    :title="document.title" :text="document.text" :source="document.source"
                    :anchorId="document.anchorId" :index="document.index" />
            </ChatDocumentGroup>
        </div>
        <div v-else>
            <div class="flex items-center justify-center">
                <p class="text-xs px-auto py-12 text-gray-500 text-center word-break">{{ t('chat.noSourcesHint') }}</p>
            </div>
        </div>
    </SideBarContainer>
</template>
