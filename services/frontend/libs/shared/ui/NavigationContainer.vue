<script lang="ts"
        setup>
      const NAV_LOGO = '/assets/navigation-logo.svg';
</script>

<template>
      <div class="bg-primary flex p-4">
            <div class="flex-1">
                  <img :src="NAV_LOGO"
                       class="w-32" />
            </div>
            <slot></slot>
      </div>
</template>
