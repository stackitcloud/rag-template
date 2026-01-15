<script lang="ts"
        setup>
        import { iconCircleCheck, iconCircleX, iconLoadingCircle, iconTriangleWarning } from "@sit-onyx/icons";
        import { UploadedDocument } from "../models/uploaded-document.model.ts";
        import { useI18n } from "vue-i18n";
        import { OnyxIcon } from "@shared/ui";
        import { computed } from "vue";
        import { formatFileSizeToString } from "@shared/utils";
        import { getDocumentIcon } from "../utils/document-icon.utils";

        const { t } = useI18n()
        const props = defineProps<{ data: UploadedDocument, removeItem: (documentId: string) => void }>();


        const progressValue = computed(() => {
            const total = props?.data?.total ?? 0;
            const progress = props?.data?.progress ?? 0;
            const value = (progress / total) * 100;
            return value.toFixed(0);
        });

        const progressText = computed(() => {
            const progressStr = formatFileSizeToString(props?.data?.progress);
            const totalStr = formatFileSizeToString(props?.data?.total);
            return `${progressStr} of ${totalStr}`;
        });

        const documentIcon = computed(() => getDocumentIcon(props.data.file.name));
</script>
<template>
    <div class="bg-base-200 rounded-box p-2 md:p-4">
        <div class="flex gap-2">
            <div class="flex items-center justify-center text-center w-10">
                <OnyxIcon :icon="documentIcon" :size="32" class="text-base-content/40" />
            </div>
            <div class="flex-1 break-words text-ellipsis overflow-hidden flex flex-col">
                <h4 class="text-sm">{{ props.data.file.name }}</h4>
                <div class="text-xs flex gap-1 mt-1">
                    <span class="opacity-50">{{ progressText }}</span>
                    <span class="opacity-50">•</span>

                    <!-- Upload processing -->
                    <span class="flex gap-1"
                          v-if="props.data.isProcessing && !props.data.isFailed && !props.data.isCompleted">
                        <OnyxIcon :icon="iconLoadingCircle" :size="16" class="text-primary animate-spin" />
                        <span> {{ t('documents.uploadProcessing') }}</span>
                    </span>

                    <!-- Upload success -->
                    <span class="flex gap-1"
                          v-if="props.data.isCompleted && !props.data.isFailed">
                        <OnyxIcon :icon="iconCircleCheck" :size="16" class="text-success" />
                        <span> {{ t('documents.uploadDocumentCompleted') }}</span>
                    </span>

                    <!-- Upload failed -->
                    <span class="flex gap-1"
                          v-if="props.data.isFailed">
                        <OnyxIcon :icon="iconTriangleWarning" :size="16" class="text-warning" />
                        <span> {{ t('documents.uploadDocumentFailed') }}</span>
                    </span>

                    <!-- Uploading -->
                    <span class="flex gap-1 justify-center"
                          v-if="!props.data.isCompleted && !props.data.isFailed && !props.data.isProcessing">
                        <span class="loading loading-spinner text-primary w-4 h-4"></span>
                        <span> {{ t('documents.uploadingDocument') }}</span>
                    </span>
                </div>
            </div>
            <div class="flex"
                 v-if="props.data.isCompleted || props.data.isFailed">
                <OnyxIcon
                    @click="props.removeItem(props.data.id)"
                    :icon="iconCircleX"
                    :size="16"
                    class="cursor-pointer hover:opacity-65 text-primary"
                />
            </div>
        </div>
        <div v-if="!data.isCompleted && progressValue != 'NaN'">
            <progress class="progress progress-primary w-full"
                      :value="progressValue"
                      max="100"></progress>
        </div>
    </div>
</template>
