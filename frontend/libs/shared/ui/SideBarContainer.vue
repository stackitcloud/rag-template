<script setup
        lang="ts">
        import { DocumentDuplicateIcon } from "@heroicons/vue/24/outline";

        const props = defineProps<{
            header: string,
            count?: number
        }>();
</script>

<template>
    <div class="h-full bg-base-100 rounded-box p-2 md:p-4 flex flex-col border">
        <div class="flex items-center mb-6 mt-2 px-2">
            <DocumentDuplicateIcon class="w-7 h-7" />
            <h1 class="ml-2 text-xl font-medium flex-1">{{ props.header }}</h1>
            <h1 class="ml-2">{{ props.count }}</h1>
        </div>

        <div class="overflow-y-auto overflow-x-hidden rounded-box flex-1"
             id="sidebarContainer">
            <slot></slot>
        </div>
    </div>
</template>
