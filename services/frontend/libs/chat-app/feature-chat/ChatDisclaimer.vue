<script lang="ts" setup>
        import { useI18n } from 'vue-i18n'
        const { t } = useI18n()
</script>

<template>
    <div class="flex gap-2 md:gap-4">
        <span class="text-xs text-gray-400">{{ t('chat.disclaimer') }}</span>
    </div>
</template>
