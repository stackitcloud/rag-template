<script lang="ts"
        setup>
        import UploadedDocumentItem from '../ui/UploadedDocumentItem.vue';
        import { useI18n } from 'vue-i18n'
        import { computed, ref } from "vue";
        import { CloudArrowUpIcon, InformationCircleIcon } from '@heroicons/vue/24/outline';
        import { useDocumentsStore } from '../data-access/+state/documents.store';
        import { UploadedDocument } from '../models/uploaded-document.model';

        const store = useDocumentsStore();
        const { t } = useI18n();
        const isDragOver = ref(false);
        const fileInputRef = ref<HTMLInputElement>();
        const uploadedDocuments = computed((): UploadedDocument[] => store.uploadedDocuments);
        const isInvalidFileType = ref(false);
        const allowedFileTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/xml'];

        const uploadDocuments = (files: File[]) => {
            if (files.some(file => !allowedFileTypes.includes(file.type))) {
                isInvalidFileType.value = true;
                return;
            }

            isInvalidFileType.value = false;
            store.uploadDocuments(files);
        }

        const onFileInputChange = (event: Event) => {
            const target = event.target as HTMLInputElement;
            const files = Array.from(target.files!);
            uploadDocuments(files);
            target.value = '';
        }

        const onDrop = (event: DragEvent) => {
            event.preventDefault();
            isDragOver.value = false;
            const files = Array.from(event.dataTransfer!.files);
            uploadDocuments(files);
        }

        const onDragOver = (event: DragEvent) => {
            event.preventDefault();
            isDragOver.value = true;
        }

        const onDragLeave = () => {
            isDragOver.value = false;
        }

        const onRemoveDocument = (documentId: string) => {
            store.removeUploadedDocument(documentId);
        }
</script>

<template>
    <div class="flex justify-center items-center min-w-full min-h-full">
        <div class="flex flex-col max-w-lg w-full">

            <!-- Drag and drop area -->
            <div class="flex flex-col m-auto justify-center items-center w-full h-64 bg-base-100 rounded-box border border-base-300 border-dashed"
                 :class="{ 'bg-base-200': isDragOver }"
                 @dragover.prevent="onDragOver"
                 @dragleave.prevent="onDragLeave"
                 @drop.prevent="onDrop">
                <div class="flex flex-col justify-center items-center pt-5 pb-6">
                    <CloudArrowUpIcon class="w-10 h-10 mb-4 text-accent-content" />
                    <p class="mb-1 font-bold text-center">{{ t('documents.uploadSelectTitle') }}</p>
                    <p class="text-xs opacity-50">{{ t('documents.uploadSelectDescription') }}</p>

                    <button class="btn btn-sm mt-4 btn-accent"
                            @click="fileInputRef!.click()">{{ t('documents.select') }}</button>
                </div>
                <input ref="fileInputRef"
                       type="file"
                       multiple
                       accept=".pdf,.docx,.pptx,.xml"
                       @change="onFileInputChange"
                       class="hidden" />
            </div>

            <!-- Uploaded documents -->
            <div class="mx-auto mt-4 w-full">
                <div class="mb-4"
                     v-for="uploadDocument in uploadedDocuments"
                     :key="uploadDocument.id">
                    <UploadedDocumentItem class="slide-in-down"
                                          :removeItem="onRemoveDocument"
                                          :data="uploadDocument" />
                </div>
            </div>

            <!-- Error message -->
            <div role="alert"
                 v-if="isInvalidFileType"
                 @click="isInvalidFileType = false"
                 class="alert alert-warning cursor-pointer mb-2 slide-in-down">
                <InformationCircleIcon class="w-6 h-6" />
                <div>
                    <h3 class="font-bold">{{ t('documents.fileTypeNotAllowedTitle') }}</h3>
                    <div class="text-xs">{{ t('documents.fileTypeNotAllowedDescription') }}</div>
                </div>
            </div>

        </div>
    </div>
</template>
<style scoped>
.slide-in-down {
    animation: slide-in-down 0.3s ease-out;
}

@keyframes slide-in-down {
    0% {
        transform: translateY(-15%);
    }

    100% {
        transform: translateY(0);
    }
}
</style>
