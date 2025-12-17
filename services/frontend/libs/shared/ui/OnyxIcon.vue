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

const sanitizeSvg = (raw: string): string => {
  const svg = raw?.trim?.() ?? "";
  if (!svg) return "";

  const stripDangerousAttrs = (input: string) =>
    input
      .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, "")
      .replace(/\s(xlink:href|href)\s*=\s*(['"])\s*javascript:[^'"]*\2/gi, "");

  // Basic allowlist: must be an inline SVG string.
  if (!svg.startsWith("<svg") || !svg.includes("</svg>")) return "";

  // Quick reject for common dangerous elements/URLs.
  if (/<script[\s>]/i.test(svg) || /<foreignObject[\s>]/i.test(svg) || /javascript:/i.test(svg)) return "";

  try {
    if (typeof DOMParser === "undefined") return stripDangerousAttrs(svg);

    const doc = new DOMParser().parseFromString(svg, "image/svg+xml");
    const root = doc.documentElement;
    if (root?.nodeName?.toLowerCase() !== "svg") return "";

    root.querySelectorAll("script, foreignObject").forEach((el) => el.remove());

    const all = [root, ...Array.from(root.querySelectorAll("*"))];
    for (const el of all) {
      for (const attr of Array.from(el.attributes)) {
        const name = attr.name.toLowerCase();
        const value = attr.value ?? "";
        if (name.startsWith("on")) {
          el.removeAttribute(attr.name);
          continue;
        }
        if ((name === "href" || name === "xlink:href") && value.trim().toLowerCase().startsWith("javascript:")) {
          el.removeAttribute(attr.name);
        }
      }
    }

    return root.outerHTML;
  } catch {
    return stripDangerousAttrs(svg);
  }
};

const sanitizedIcon = computed(() => sanitizeSvg(props.icon));

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
    v-html="sanitizedIcon"
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
