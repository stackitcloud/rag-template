<script setup lang="ts">
import { iconFile } from "@sit-onyx/icons";
import OnyxIcon from "./OnyxIcon.vue";

const props = withDefaults(
  defineProps<{
    header: string;
    count?: number;
    showBorder?: boolean;
  }>(),
  {
    showBorder: true,
  },
);
</script>

<template>
  <div
    :class="[
      'h-full bg-base-100 flex flex-col p-2 md:p-2',
      props.showBorder ? 'border-l-2 border-base-300' : '',
    ]"
  >
    <div class="flex items-center mb-6 mt-2 px-2">
      <OnyxIcon :icon="iconFile" :size="28" />
      <h1 class="ml-2 text-xl font-medium flex-1">{{ props.header }}</h1>
      <h1 v-if="props.count !== undefined" class="ml-2">{{ props.count }}</h1>
      <div class="ml-2 flex items-center gap-1">
        <slot name="header-actions"></slot>
      </div>
    </div>

    <div class="overflow-y-auto overflow-x-hidden rounded-box flex-1" id="sidebarContainer">
      <slot></slot>
    </div>
  </div>
</template>
<!-- <style scoped lang="css">
  .side-bar-container {
    box-shadow: ;
  }
</style> -->
