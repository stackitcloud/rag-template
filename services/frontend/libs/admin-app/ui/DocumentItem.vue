<script lang="ts" setup>
import { DocumentIcon, XCircleIcon, ArrowUpTrayIcon, ArrowPathIcon, ExclamationTriangleIcon, CheckCircleIcon } from "@heroicons/vue/24/outline";
import { ref } from "vue";
import { DocumentModel } from "../models/document.model";

const hover = ref(false);

const props = defineProps<{ data: DocumentModel, deleteDocument: (documentId: string) => void }>();

const onDeleteDocument = () => {
    props.deleteDocument(props.data.name);
}
</script>
<template>
    <div class="bg-base-200 rounded-box p-2 md:p-4 flex gap-2">
        <div class="flex items-center justify-center text-center w-8">
            <DocumentIcon class="w-10 h-10 opacity-60" />
        </div>
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col justify-center">
            <h4 class="font-medium">{{ props.data.name }}</h4>
        </div>
        <div class="flex items-center justify-center" @mouseover="hover = true" @mouseleave="hover = false">
            <div v-if="props.data.status === 'UPLOADING'">
                <ArrowUpTrayIcon class="w-6 h-6 opacity-65" />
            </div>
            <div v-else-if="props.data.status === 'PROCESSING'">
                <ArrowPathIcon class="w-6 h-6 opacity-65 rotating" />
            </div>
            <div v-else-if="hover">
                <XCircleIcon @click="onDeleteDocument" class="w-6 h-6 opacity-65 cursor-pointer hover:opacity-65" />
            </div>
            <div v-else-if="props.data.status === 'READY'">
                <CheckCircleIcon class="w-6 h-6 opacity-65" />
            </div>
            <div v-else>
                <ExclamationTriangleIcon class="w-6 h-6 opacity-65" />
            </div>
        </div>
    </div>
</template>
<style scoped>
.rotating {
  animation: rotationAnimation 2s linear infinite;
}
@keyframes rotationAnimation {
 0%{
    transform: rotate(0deg);
   }
100%{
    transform: rotate(360deg);
   }
}
</style>
