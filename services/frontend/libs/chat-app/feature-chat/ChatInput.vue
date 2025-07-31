<script lang="ts" setup>
import { useI18n } from 'vue-i18n'
import { onMounted, ref, computed } from 'vue'
import { useChatStore } from "../data-access/+state/chat.store"
import { PaperAirplaneIcon } from '@heroicons/vue/24/outline'

const chatStore = useChatStore()
const { t } = useI18n()
const textareaRef = ref<HTMLTextAreaElement>()
const isLoading = computed(() => chatStore.isLoading)

const onCallInference = async (event: Event) => {
  event.preventDefault()
  const textarea = textareaRef.value
  if (!textarea || !textarea.value.trim()) {
    return
  }

  try {
    await chatStore.callInference(textarea.value)
  } catch (e) {
    console.error(e)
  } finally {
    textarea.value = ''
    adjustTextareaHeight()
    textarea.focus()
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    onCallInference(event)
  }
}

const adjustTextareaHeight = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = '40px' // Reset to auto
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    textarea.style.overflowY = textarea.scrollHeight > 120 ? 'auto' : 'hidden'
  }
}

const props = defineProps<{
  isDisabled: boolean
}>()

onMounted(() => {
  textareaRef.value?.focus()
  adjustTextareaHeight()
})
</script>

<template>
  <div class="flex bg-base-200 rounded-box gap-2 items-center">
    <textarea
      ref="textareaRef"
      required
      :disabled="props.isDisabled"
      :placeholder="t('chat.justAsk')"
      @keydown="handleKeyDown"
      @input="adjustTextareaHeight"
      class="flex-1 bg-base-200 input min-h-[40px] max-h-[120px] resize-none outline-none focus:outline-none focus:border-none py-2 px-3"
    ></textarea>

    <button
      type="button"
      @click="onCallInference"
      class="btn btn-accent h-10 self-end"
      :disabled="props.isDisabled"
    >
      <div v-if="isLoading" class="text-center">
        <span class="loading loading-spinner w-4 h-4"></span>
      </div>

      <div v-else class="flex gap-2 justify-center items-center">
        <PaperAirplaneIcon class="w-4 h-4" />
      </div>
    </button>
  </div>
</template>

<style scoped>
textarea {
  line-height: 1.5rem;
  overflow-y: hidden;
}

textarea::placeholder {
  line-height: 1.5rem;
}

textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.7);
}
</style>