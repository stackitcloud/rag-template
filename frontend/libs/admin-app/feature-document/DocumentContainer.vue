<script lang="ts"
        setup>
        import DocumentItem from '../ui/DocumentItem.vue';
        import { useI18n } from 'vue-i18n';
        import { SideBarContainer } from '@shared/ui';
        import { useDocumentsStore } from '../data-access/+state/documents.store.ts';
        import { computed, watch } from 'vue';
        import { DocumentModel } from '../models/document.model.ts';

        const { t } = useI18n();
        const store = useDocumentsStore();
        const documents = computed(() => store.allDocuments);

        const deleteDocument = (documentId: string) => {
            store.deleteDocument(documentId);
        };

        const highlightNewDocuments = (newDocs: DocumentModel[], oldDocs: DocumentModel[]) => {
            const newDocumentIds = newDocs.map(doc => doc.id).filter(id => !oldDocs.some(doc => doc.id === id));
            highlightDocumentsById(newDocumentIds);
        };

        const highlightDocumentsById = (documentIds: string[]) => {
            setTimeout(() => { // wait for the DOM to update
                documentIds.forEach(id => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.classList.add('base-200-highlight', 'slide-in-right');
                        setTimeout(() => element.classList.remove('base-200-highlight', 'slide-in-right'), 2000);
                    }
                });
            });
        };

        watch(documents, (newDocs, oldDocs) => {
            if (oldDocs && newDocs && newDocs.length > oldDocs.length) {
                highlightNewDocuments(newDocs, oldDocs);
            }
        }, { deep: true });

</script>
<template>
    <SideBarContainer :header="t('documents.files')"
                      :count="documents?.length ?? 0">
        <DocumentItem v-for="document in documents"
                      class="mb-2 md:mb-4"
                      :id="document.id"
                      :key="document.id"
                      :deleteDocument="deleteDocument"
                      :data="document" />
    </SideBarContainer>
</template>
<style scoped>
.slide-in-right {
    animation: slide-in-right 0.3s ease-out;
}

@keyframes slide-in-right {
    0% {
        transform: translateX(100%);
    }

    100% {
        transform: translateX(0);
    }
}
</style>