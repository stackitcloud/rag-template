<script lang="ts"
        setup>
        import { useI18n } from 'vue-i18n'
        import { onMounted, ref } from 'vue'
        import { useChatStore } from "../data-access/+state/chat.store";
        import { computed } from "vue";
        import { PaperAirplaneIcon } from '@heroicons/vue/24/outline';

        const chatStore = useChatStore();
        const { t } = useI18n()
        const inputRef = ref<HTMLInputElement>()
        const isLoading = computed(() => chatStore.isLoading)

        const onCallInference = async (event: Event) => {
            event.preventDefault();

            const input = inputRef.value;
            if (input == null || input.value == null) {
                return
            }

            try {
                await chatStore.callInference(input.value)
            } catch (e) {
                console.error(e)
            } finally {
                input.value = ''
                input.focus()
            }
        }

        const props = defineProps<{
            isDisabled: boolean
        }>()

        onMounted(() => {
            inputRef.value?.focus()
        })
</script>

<template>
    <div class="flex gap-2 md:gap-4 p-2 md:p-8 rounded-box border">
        <input type="text"
               ref="inputRef"
               required
               :disabled="props.isDisabled"
               :placeholder="t('chat.justAsk')"
               @keydown.enter="onCallInference"
               class="input bg-base-200 flex-1 focus:border-base-300 " />

        <button type="button"
                @click="onCallInference"
                class="btn btn-accent w-10 md:w-32"
                :disabled="props.isDisabled">
            <div v-if="isLoading"
                 class="text-center">
                <span class="loading loading-spinner w-4 h-4"></span>
            </div>

            <div v-else
                 class="flex gap-2 justify-center items-center">
                <PaperAirplaneIcon class="w-4 h-4" />
                <span class="hidden md:block">{{ t('chat.send') }}</span>
            </div>
        </button>
    </div>
</template>