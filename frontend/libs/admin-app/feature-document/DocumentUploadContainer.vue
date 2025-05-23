<script lang="ts" setup>
import { CloudArrowUpIcon, GlobeAltIcon, InformationCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { computed, ref } from "vue";
import { useI18n } from 'vue-i18n';
import { useDocumentsStore } from '../data-access/+state/documents.store';
import { UploadedDocument } from '../models/uploaded-document.model';
import UploadedDocumentItem from '../ui/UploadedDocumentItem.vue';

const store = useDocumentsStore();
const {t} = useI18n();
const isDragOver = ref(false);
const fileInputRef = ref<HTMLInputElement>();
const uploadedDocuments = computed((): UploadedDocument[] => store.uploadedDocuments);
const isInvalidFileType = ref(false);
const allowedFileTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/xml'];
const uploadMethod = ref<'file' | 'confluence'>('file');


// confluence configuration refs
const confluenceName = ref('');
const spaceKey = ref('');
const confluenceToken = ref('');
const confluenceUrl = ref('');
const maxPages = ref<number>();

const error = computed(() => store.error);

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

const handleConfluenceUpload = () => {
    // send configured parameters to backend
    store.loadConfluence({
        name: confluenceName.value,
        spaceKey: spaceKey.value,
        token: confluenceToken.value,
        url: confluenceUrl.value,
        maxPages: maxPages.value
    });
}

const clearError = () => {
    store.error = null
}

const getErrorMessage = (errorType: string) => {
    switch (errorType) {
        case 'delete':
            return t('documents.deleteError');
        case 'upload':
            return t('documents.uploadError');
        case 'load':
            return t('documents.loadError');
        case 'confluence':
            return t('documents.confluenceError');
        case 'confluence_not_configured':
            return t('documents.confluenceNotConfigured');
        case 'confluence_locked':
            return t('documents.confluenceLocked');
        default:
            return t('documents.unknownError');
    }
}
</script>

<template>
    <div class="flex justify-center items-center min-w-full min-h-full">
        <div class="flex flex-col w-full max-w-3xl">
            <!-- Error message -->
            <div v-if="error" role="alert"
                class="alert alert-error mb-4 slide-in-down flex justify-between items-center">
                <div class="flex items-center">
                    <InformationCircleIcon class="w-6 h-6 mr-2" />
                    <div>
                        <h3 class="font-bold">{{ t('documents.errorOccurred') }}</h3>
                        <div class="text-sm">{{ getErrorMessage(error) }}</div>
                    </div>
                </div>
                <button @click="clearError" class="btn btn-ghost btn-sm">
                    <XMarkIcon class="w-5 h-5" />
                </button>
            </div>

            <!-- Upload method tabs -->
            <div class="tabs tabs-boxed mb-4">
                <a class="tab" :class="{'tab-active': uploadMethod === 'file'}" @click="uploadMethod = 'file'">
                    {{ t('documents.fileUpload') }}
                </a>
                <a class="tab" :class="{'tab-active': uploadMethod === 'confluence'}"
                    @click="uploadMethod = 'confluence'">
                    {{ t('documents.confluenceUpload') }}
                </a>
            </div>

            <!-- File upload area -->
            <div v-if="uploadMethod === 'file'"
                class="flex flex-col m-auto justify-center items-center w-full h-96 bg-base-100 rounded-box border border-base-300 border-dashed"
                :class="{'bg-base-200': isDragOver}" @dragover.prevent="onDragOver" @dragleave.prevent="onDragLeave"
                @drop.prevent="onDrop">
                <div class="flex flex-col justify-center items-center pt-5 pb-6">
                    <CloudArrowUpIcon class="w-10 h-10 mb-4 text-accent-content" />
                    <p class="mb-1 font-bold text-cente">{{ t('documents.uploadSelectTitle') }}</p>
                    <p class="text-xs opacity-50">{{ t('documents.uploadSelectDescription') }}</p>

                    <button class="btn btn-sm mt-4 btn-accent" @click="fileInputRef!.click()">{{ t('documents.select')
                        }}</button>
                </div>
                <input ref="fileInputRef" type="file" multiple accept=".pdf,.docx,.pptx,.xml" @change="onFileInputChange"
                    class="hidden" />
            </div>

            <!-- Confluence load area -->
            <div v-else
                class="flex flex-col m-auto justify-center items-center w-full h-112 bg-base-100 rounded-box border border-base-300">
                <div class="flex flex-col justify-center items-center pt-5 pb-6">
                    <GlobeAltIcon class="w-10 h-10 mb-4 text-accent-content" />
                    <p class="mb-1 font-bold">{{ t('documents.confluenceLoadTitle') }}</p>
                    <!-- configuration inputs -->
                    <div class="space-y-2 mb-4 w-full max-w-sm">
                      <input v-model="confluenceUrl" type="url" placeholder="URL" class="input input-bordered w-full" />
                      <input v-model="confluenceName" type="text" placeholder="Name" class="input input-bordered w-full" />
                      <input v-model="spaceKey" type="text" placeholder="Space key" class="input input-bordered w-full" />
                      <input v-model="confluenceToken" type="password" placeholder="Token" class="input input-bordered w-full" />
                      <input v-model.number="maxPages" type="number" placeholder="Max number of pages" class="input input-bordered w-full" />
                    </div>
                    <p class="text-xs opacity-50 mb-4">{{ t('documents.confluenceLoadDescription') }}</p>
                    <button class="btn btn-sm btn-accent" @click="handleConfluenceUpload">
                        {{ t('documents.loadConfluence') }}
                    </button>
                </div>
            </div>

            <!-- Uploaded documents -->
            <div class="mx-auto mt-4 w-full">
                <div class="mb-4" v-for="uploadDocument in uploadedDocuments" :key="uploadDocument.id">
                    <UploadedDocumentItem class="slide-in-down" :removeItem="onRemoveDocument" :data="uploadDocument" />
                </div>
            </div>

            <!-- Invalid file type message -->
            <div role="alert" v-if="isInvalidFileType" @click="isInvalidFileType = false"
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
