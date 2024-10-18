<script lang="ts"
        setup>
        import { RouterView } from 'vue-router'
        import { LogoContainer, NavigationContainer } from '@shared/ui'
        import { useI18n } from 'vue-i18n';
        import { ArrowTopRightOnSquareIcon } from '@heroicons/vue/24/outline';

        const { t } = useI18n();
        const adminURL = import.meta.env.VITE_ADMIN_URL;
</script>

<template>
  <main class="bg-base-100 flex flex-col">
    <NavigationContainer>
      <a class="flex gap-2 items-center btn btn-primary border border-opacity-10 border-white btn-sm"
         target="_blank"
         :href="adminURL">
        <ArrowTopRightOnSquareIcon class="w-4 h-4" />
        {{ t('chat.documents') }}
      </a>
    </NavigationContainer>
    <RouterView class="flex-1 overflow-hidden" />
  </main>
</template>

<style lang="css">
@import '@shared/style';
</style>
