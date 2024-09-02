<script lang="ts"
        setup>
        import ChatDocumentItem from './ChatDocumentItem.vue';
        import { computed } from "vue";
        import { useI18n } from 'vue-i18n';
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

        const documents = computed((): ChatDocumentItemModel[] => {
            return props.documents.map((message) => mapToDocumentItem(message));
        });
</script>
<template>
    <SideBarContainer :header="t('chat.sources')">
        <div v-if="documents.length > 0">
            <ChatDocumentItem v-for="document in documents"
                              :key="document.index"
                              :id="document.index"
                              :title="document.title"
                              :text="document.text"
                              :source="document.source"
                              :anchorId="document.anchorId"
                              :index="document.index" />
        </div>
        <div v-else>
            <!--To be defined-->
        </div>
    </SideBarContainer>
</template>