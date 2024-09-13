<script lang="ts" setup>
import { ArrowTopRightOnSquareIcon, DocumentIcon } from "@heroicons/vue/24/outline";
import { ChatDocumentGroupModel } from "../models/chat-document-group.model";

const data = defineProps<ChatDocumentGroupModel>();
</script>
<template>
    <div class="border-b py-2 md:py-4 px-4 flex gap-4">
        <!-- <div class="flex items-center">
            <div class="rounded-full p-4 bg-base-200">
                <DocumentIcon class="w-4 h-4 text-primary" />
            </div>
        </div> -->
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col">
            <h4 class="font-medium flex items-center gap-2 mb-1">
                {{ data.title }}

                <a class="text-sm text-primary cursor-pointer hover:opacity-75" :href="data.source" target="_blank">
                    <ArrowTopRightOnSquareIcon class="h-4 w-4" />
                </a>
            </h4>
            <slot></slot>
        </div>
    </div>
</template>
