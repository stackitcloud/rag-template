<script lang="ts"
        setup>
        import { DocumentIcon, XCircleIcon } from "@heroicons/vue/24/outline";
        import { DocumentModel } from "../models/document.model.ts";

        const props = defineProps<{ data: DocumentModel, deleteDocument: (documentId: string) => void }>();

        const onDeleteDocument = () => {
            props.deleteDocument(props.data.id);
        }
</script>
<template>
    <div class="bg-base-200 rounded-box p-2 md:p-4 flex gap-2">
        <div class="flex items-center justify-center text-center w-8">
            <DocumentIcon class="w-10 h-10 opacity-60" />
        </div>
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col justify-center">
            <h4 class="font-medium">{{ props.data.id }}</h4>
        </div>
        <div class="flex items-center justify-center">
            <XCircleIcon @click="onDeleteDocument"
                       class="w-6 h-6 opacity-65 cursor-pointer hover:opacity-65" />
        </div>
    </div>
</template>