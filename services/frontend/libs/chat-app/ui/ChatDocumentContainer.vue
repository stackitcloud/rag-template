<script lang="ts" setup>
import ChatDocumentItem from './ChatDocumentItem.vue';
import ChatDocumentGroup from './ChatDocumentGroup.vue';
import { computed } from "vue";
import { useI18n } from 'vue-i18n';
import { isNotEmpty } from '@shared/utils';
import { ChatDocumentItemModel, mapToDocumentItem } from '../models/chat-document-item.model';
import { SideBarContainer } from '@shared/ui';
import { ChatDocumentModel } from '../models/chat-document.model';

const { t } = useI18n()

const props = defineProps<{
    documents: Array<ChatDocumentModel>
}>()

const groupedDocuments = computed((): Record<string, ChatDocumentItemModel[]> => {
    const items = props.documents.map((document) => mapToDocumentItem(document));
    return items.reduce((acc: Record<string, ChatDocumentItemModel[]>, element: ChatDocumentItemModel) => {
        if (!acc[element.title]) acc[element.title] = [];
        acc[element.title].push(element);
        return acc;
    }, {});
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
