<script lang="ts"
        setup>
        import { ArrowTopRightOnSquareIcon, DocumentIcon } from "@heroicons/vue/24/outline";
        import { ChatDocumentItemModel } from "../models/chat-document-item.model";

        const data = defineProps<ChatDocumentItemModel>();

        const scrollReveal = (anchorId: string) => {
            const item = document.getElementById(anchorId);
            if (item) {
                item.classList.add("opacity-75");
                item.scrollIntoView({ behavior: 'smooth', block: 'start' });

                setTimeout(() => {
                    item?.classList?.remove("opacity-75");
                }, 2000);
            }
        }
</script>
<template>
    <div class="border-b py-2 md:py-4 pr-4  flex gap-4"
         :id="data.index.toString()">
        <div class="flex items-center">
            <div class="rounded-full p-4 bg-base-200">
                <DocumentIcon class="w-4 h-4 text-primary" />
            </div>
        </div>
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col">
            <h4 class="font-medium flex items-center gap-2 mb-1">
                {{ data.title }}

                <a class="text-sm text-primary cursor-pointer hover:opacity-75"
                   :href="data.source"
                   target="_blank">
                    <ArrowTopRightOnSquareIcon class="h-4 w-4" />
                </a>
            </h4>
            <div class="text-xs">
                <a class="text-info cursor-pointer hover:opacity-75 text-md"
                   @click="scrollReveal(data.anchorId.toString())">
                    [{{ data.index }}]
                </a>
                <span v-html="data.text"></span>
            </div>
        </div>
    </div>
</template>