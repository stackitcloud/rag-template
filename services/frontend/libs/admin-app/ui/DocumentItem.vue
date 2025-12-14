<script lang="ts" setup>
import {
  iconCircleCheck,
  iconSync,
  iconTrash,
  iconTriangleWarning,
  iconUpload,
} from "@sit-onyx/icons";
import { OnyxIcon } from "@shared/ui";
import { computed, ref } from "vue";
import { DocumentModel } from "../models/document.model";
import { getDocumentIcon } from "../utils/document-icon.utils";

const showDeleteModal = ref(false);

const props = defineProps<{
  data: DocumentModel;
  deleteDocument: (documentId: string) => void;
}>();

// Deletion is not allowed while a document is in PROCESSING state
const PROCESSING_STATE = "PROCESSING";
const isProcessing = computed(() => props.data.status === PROCESSING_STATE);
const canDelete = computed(() => !isProcessing.value);

const statusClasses = {
  UPLOADING: "text-info",
  PROCESSING: "text-warning",
  READY: "text-success",
  ERROR: "text-error",
};

const statusText = {
  UPLOADING: "Uploading",
  PROCESSING: "Processing",
  READY: "Ready",
  ERROR: "Error",
};

const documentIcon = computed(() => getDocumentIcon(props.data.name));

const confirmDelete = () => {
  if (!canDelete.value) return; // Guard against accidental triggers
  showDeleteModal.value = true;
};

const cancelDelete = () => {
  showDeleteModal.value = false;
};

const executeDelete = () => {
  props.deleteDocument(props.data.name);
  showDeleteModal.value = false;
};
</script>

<template>
  <div
    class="bg-base-200 rounded-box p-3 md:p-4 flex flex-wrap gap-3 transition-all duration-200 hover:bg-base-300"
  >
    <!-- Document icon -->
    <div class="flex items-center justify-center text-center w-10">
      <OnyxIcon :icon="documentIcon" :size="32" class="opacity-60" />
    </div>

    <!-- Document info -->
    <div class="flex-1 min-w-0 flex flex-col justify-center">
      <h4 class="font-medium text-sm md:text-base truncate">
        {{ props.data.name }}
      </h4>
      <p class="text-xs text-opacity-75 text-base-content truncate">
        <!-- You can add more document metadata here -->
        <!-- For example: Uploaded on {{ formatDate(props.data.uploadDate) }} -->
      </p>
    </div>

    <!-- Status indicator -->
    <div
      class="flex items-center gap-2 px-2"
      :class="statusClasses[props.data.status]"
    >
      <div v-if="props.data.status === 'UPLOADING'">
        <OnyxIcon :icon="iconUpload" :size="20" />
      </div>
      <div v-else-if="props.data.status === 'PROCESSING'">
        <OnyxIcon :icon="iconSync" :size="20" class="rotating" />
      </div>
      <div v-else-if="props.data.status === 'READY'">
        <OnyxIcon :icon="iconCircleCheck" :size="20" />
      </div>
      <div v-else>
        <OnyxIcon :icon="iconTriangleWarning" :size="20" />
      </div>
      <span class="text-xs font-medium hidden sm:inline">{{
        statusText[props.data.status]
      }}</span>
    </div>

    <!-- Actions -->
    <div class="flex items-center">
      <button
        @click="confirmDelete"
        :disabled="!canDelete"
        :aria-disabled="!canDelete"
        data-testid="document-delete-btn"
        class="btn btn-sm btn-ghost btn-circle opacity-60 hover:opacity-100 disabled:opacity-30 disabled:cursor-not-allowed"
        aria-label="Delete document"
      >
        <OnyxIcon :icon="iconTrash" :size="16" :class="canDelete ? 'text-error' : 'opacity-40'" />
      </button>
    </div>
  </div>

  <!-- Delete confirmation modal -->
  <div
    v-if="showDeleteModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    role="dialog"
    aria-modal="true"
    aria-labelledby="delete-modal-title"
  >
    <div class="bg-base-100 p-6 rounded-box max-w-md w-full">
      <h3 id="delete-modal-title" class="font-bold text-lg mb-4">Confirm Deletion</h3>
      <p class="mb-4">
        Are you sure you want to delete
        <span class="font-semibold">{{ props.data.name }}</span
        >? This action cannot be undone.
      </p>
      <div class="flex justify-end gap-2">
        <button @click="cancelDelete" class="btn btn-ghost">Cancel</button>
        <button @click="executeDelete" class="btn btn-error">Delete</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rotating {
  animation: rotationAnimation 2s linear infinite;
}
@keyframes rotationAnimation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
