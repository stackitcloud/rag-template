<script lang="ts"
        setup>
        import DocumentContainer from './DocumentContainer.vue';
        import DocumentUploadContainer from './DocumentUploadContainer.vue';
        import { useDocumentsStore } from '../data-access/+state/documents.store';
        import { useI18n } from 'vue-i18n';
        import { onMounted } from 'vue';

        const { t } = useI18n();
        const documentStore = useDocumentsStore();

        onMounted(() => {
            documentStore.loadDocuments();
        });
</script>

<template>
    <div data-testid="document-view"
         class="md:container md:mx-auto h-full p-4 flex gap-4">
        <div class="flex-1 flex">
            <div class="flex flex-1 flex-col">
                <div class="flex gap-4 items-center p-4 pt-6">
                    <div class="flex flex-col flex-1">
                        <div class="font-medium">{{ t('documents.uploadDocuments') }}</div>
                        <div class="text-sm opacity-50">{{ t('documents.uploadDocumentsInfo') }}</div>
                    </div>
                </div>
                <div class="overflow-y-auto overflow-x-hidden h-full p-2 md:p-4">
                    <DocumentUploadContainer />
                </div>
            </div>
        </div>
        <div class="overflow-y-auto w-full md:w-4/12">
            <DocumentContainer />
        </div>
    </div>
</template>