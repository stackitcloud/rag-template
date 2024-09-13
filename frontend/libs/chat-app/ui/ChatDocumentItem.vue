<script lang="ts" setup>
// import { ArrowTopRightOnSquareIcon, DocumentIcon } from "@heroicons/vue/24/outline";
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
    <div class="pt-1 pr-2 flex gap-4" :id="data.index.toString()">
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col">
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
