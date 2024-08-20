<script lang="ts"
        setup>
      const LEFT_LOGO = '/assets/sub-header-left-logo.svg';
      const RIGHT_LOGO = '/assets/sub-header-right-logo.svg';
</script>

<template>
      <div class="bg-base-200">
            <div class="md:container md:mx-auto flex p-4">
                  <div class="flex-1">
                        <img :src="LEFT_LOGO"
                             class="w-40" />
                  </div>
                  <img :src="RIGHT_LOGO" />
            </div>
      </div>
</template>
