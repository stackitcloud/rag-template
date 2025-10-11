<script setup lang="ts">
import { SideBarContainer } from '@shared/ui';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

type AddressDoc = { title: string; url: string };

const props = defineProps<{ documents: AddressDoc[] }>();

const count = computed(() => props.documents?.length ?? 0);
</script>

<template>
  <SideBarContainer :header="t('chat.addressDocuments')" :count="count">
    <div v-if="count > 0" class="space-y-2 pr-2">
      <div v-for="(doc, idx) in documents" :key="idx" class="truncate">
        <a class="link link-primary" :href="doc.url" target="_blank" rel="noopener noreferrer">
          {{ doc.title }}
        </a>
      </div>
    </div>
    <div v-else class="flex items-center justify-center">
      <p class="text-xs px-auto py-6 text-gray-500 text-center">{{ t('chat.noAddressDocs') }}</p>
    </div>
  </SideBarContainer>
</template>
