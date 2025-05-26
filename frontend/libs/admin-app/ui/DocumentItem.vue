<script lang="ts" setup>
import {
  DocumentIcon,
  ArrowUpTrayIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  TrashIcon,
} from "@heroicons/vue/24/outline";
import { ref } from "vue";
import { DocumentModel } from "../models/document.model";

const showDeleteModal = ref(false);

const props = defineProps<{
  data: DocumentModel;
  deleteDocument: (documentId: string) => void;
}>();

const statusClasses = {
  UPLOADING: "text-blue-500",
  PROCESSING: "text-amber-500",
  READY: "text-green-500",
  ERROR: "text-red-500",
};

const statusText = {
  UPLOADING: "Uploading",
  PROCESSING: "Processing",
  READY: "Ready",
  ERROR: "Error",
};

const confirmDelete = () => {
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
      <DocumentIcon class="w-8 h-8 opacity-60" />
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
        <ArrowUpTrayIcon class="w-5 h-5" />
      </div>
      <div v-else-if="props.data.status === 'PROCESSING'">
        <ArrowPathIcon class="w-5 h-5 rotating" />
      </div>
      <div v-else-if="props.data.status === 'READY'">
        <CheckCircleIcon class="w-5 h-5" />
      </div>
      <div v-else>
        <ExclamationTriangleIcon class="w-5 h-5" />
      </div>
      <span class="text-xs font-medium hidden sm:inline">{{
        statusText[props.data.status]
      }}</span>
    </div>

    <!-- Actions -->
    <div class="flex items-center">
      <button
        @click="confirmDelete"
        class="btn btn-sm btn-ghost btn-circle opacity-60 hover:opacity-100"
        aria-label="Delete document"
      >
        <TrashIcon class="w-4 h-4 text-error" />
      </button>
    </div>
  </div>

  <!-- Delete confirmation modal -->
  <div
    v-if="showDeleteModal"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-base-100 p-6 rounded-box max-w-md w-full">
      <h3 class="font-bold text-lg mb-4">Confirm Deletion</h3>
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
