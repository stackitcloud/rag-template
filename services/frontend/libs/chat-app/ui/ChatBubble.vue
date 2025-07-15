<script lang="ts"
        setup>
        import { DocumentIcon } from '@heroicons/vue/24/outline';
import { ChatBubbleModel } from '../models/chat-bubble.model';

        const props = defineProps<ChatBubbleModel>()

        const scrollReveal = (anchorId: string) => {
            const item = document.getElementById(anchorId);
            if (item) {
                item.classList.add("base-200-highlight");
                item.scrollIntoView({ behavior: 'smooth', block: 'start' });

                setTimeout(() => {
                    item?.classList?.remove("base-200-highlight");
                }, 3000);
            }
        }
</script>

<template>
    <div :class="[
        'chat overflow-hidden',
        {
            'chat-start slide-in-left': props.align === 'left',
            'chat-end slide-in-right': props.align === 'right',
        }
    ]">
        <div class="chat-image avatar">
            <div class="w-10 rounded-full">
                <img :src="props.avatarSrc" />
            </div>
        </div>
        <div class="chat-header">
            {{ props.name }}
            <time class="text-xs opacity-50">{{ props.time }}</time>
        </div>
        <div class="chat-bubble"
             :id="props.id"
             :class="[props.backgroundColor, props.textColor]">

            <div v-if="props.text !== undefined"
                 class="flex flex-col">
                <article :class="['flex-1', 'text-pretty', 'break-words', 'prose', 'prose-sm', 'max-w-none', 'chat-text', props.proseDark]"
                   v-html="props.text"></article>

                <!-- Document jump anchors-->
                <div v-if="props.anchorIds !== undefined"
                     class="flex gap-3 text-info text-sm cursor-pointer mt-2">
                    <div class="flex items-center"
                         v-for="anchorId in anchorIds"
                         :key="anchorId"
                         @click="scrollReveal(anchorId.toString())">
                        <DocumentIcon class="w-4 h-4 mr-1" />
                        {{ anchorId }}
                    </div>
                </div>
            </div>
            <span v-else
                  class="jumping-dots text-lg">
                <span class="dot-1">.</span>
                <span class="dot-2">.</span>
                <span class="dot-3">.</span>
            </span>
        </div>
    </div>

</template>

<style scoped
       lang="css">
    .chat-text > * {
        word-break: break-all;
        overflow-wrap: break-word;
        white-space: break-spaces;
        flex-wrap: wrap;
    }

    .jumping-dots span {
        position: relative;
        bottom: 0px;
        animation: jump 1s infinite;
    }

    .jumping-dots .dot-1 {
        animation-delay: 100ms;
    }

    .jumping-dots .dot-2 {
        animation-delay: 200ms;
    }

    .jumping-dots .dot-3 {
        animation-delay: 400ms;
    }

    @keyframes jump {
        0% {
            bottom: 0px;
        }

        20% {
            bottom: 5px;
        }

        40% {
            bottom: 0px;
        }
    }

    .slide-in-right {
        animation: slide-in-right 0.5s both;
    }

    @keyframes slide-in-right {
        0% {
            transform: translateX(30px);
            opacity: 0;
        }

        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .slide-in-left {
        animation: slide-in-left 0.5s both;
    }

    @keyframes slide-in-left {
        0% {
            transform: translateX(-30px);
            opacity: 0;
        }

        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }
</style>
