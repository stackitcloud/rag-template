<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    icon: string;
    size?: number | string;
    ariaLabel?: string;
  }>(),
  {
    size: 20,
  },
);

const sizeStyle = computed(() => {
  const size = typeof props.size === "number" ? `${props.size}px` : props.size;
  return { width: size, height: size };
});

const ariaAttrs = computed(() => {
  if (props.ariaLabel) {
    return { role: "img", "aria-label": props.ariaLabel };
  }
  return { "aria-hidden": true };
});
</script>

<template>
  <span
    class="onyx-icon inline-flex shrink-0"
    :style="sizeStyle"
    v-bind="ariaAttrs"
    v-html="props.icon"
  ></span>
</template>

<style scoped>
.onyx-icon :deep(svg) {
  width: 100%;
  height: 100%;
  display: block;
  fill: currentColor;
}
</style>
