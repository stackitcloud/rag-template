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
    <div class="pt-2 pr-2 flex gap-4 hover:opacity-75" :id="data.index.toString()">
        <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col">
            <div class="text-xs" @click="scrollReveal(data.anchorId.toString())">
                <a class="text-info cursor-pointer hover:opacity-75 text-md">
                    [{{ data.index }}]
                </a>
                <article class="document-text flex-1 text-pretty break-words prose prose-sm max-w-none" v-html="data.text"></article>
            </div>
        </div>
    </div>
</template>
<style lang="css">
.document-text h1, .document-text h2, .document-text h3, .document-text h4 {
  font-size: small;
}
.document-text > * {
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: break-spaces;
    flex-wrap: wrap;
}
</style>
