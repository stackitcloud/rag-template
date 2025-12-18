<script lang="ts" setup>
import { iconArrowSmallUpRightTop } from "@sit-onyx/icons";
import { OnyxIcon } from "@shared/ui";
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
            <h2 class="font-medium mb-1">
                <a class="font-bold font-underline hover:opacity-75 flex items-center gap-2" :href="data.source" target="_blank">
                    {{ data.title }}
                    <OnyxIcon :icon="iconArrowSmallUpRightTop" :size="16" class="text-sm text-primary cursor-pointer" />
                </a>
            </h2>
            <slot></slot>
        </div>
    </div>
</template>
