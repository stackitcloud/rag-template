<script lang="ts" setup>
import ChatInput from "./ChatInput.vue";
import ChatMessages from "../ui/ChatMessages.vue";
import ChatDisclaimer from "./ChatDisclaimer.vue";
import { useChatStore } from "../data-access/+state/chat.store";
import ChatDocumentContainer from "../ui/ChatDocumentContainer.vue";
import { onMounted, onBeforeUnmount, watch } from "vue";
import { newUid } from "@shared/utils";
import { useRoute } from "vue-router";
import { addresses, type AddressData } from "@shared/portal-address";
// import { marked } from "marked"; // not needed for address docs list

const chatStore = useChatStore();

const route = useRoute();

import { ref } from "vue";
// Selected address data used to render the header documents section
const selectedAddress = ref<AddressData | null>(null);

function formatLboLabel(lboPath: string): string {
  // Expect filenames like: /assets/LBO/LBO_2019-12-04.pdf
  const m = lboPath.match(/LBO_(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return "LBO";
  const [_, y, mo, d] = m;
  const months = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
  ];
  const monthName = months[Number(mo) - 1] ?? mo;
  const day = String(Number(d)).padStart(2, "0");
  return `LBO vom ${day}. ${monthName} ${y}`;
}

let initialized = false;
function applyAddressFromRoute() {
  const addr = (route.query.addr as string) || "";
  if (!addr) {
    selectedAddress.value = null;
    return;
  }
  const selected: AddressData | undefined = addresses.find(
    (a: AddressData) => a.original === addr
  );
  if (!selected) {
    selectedAddress.value = null;
    return;
  }
  // Start a fresh conversation each time address changes
  chatStore.resetConversation(newUid());
  selectedAddress.value = selected;
}

onMounted(async () => {
  if (!initialized) {
    chatStore.initiateConversation(newUid());
    initialized = true;
  }
  applyAddressFromRoute();
});

watch(
  () => route.query.addr,
  () => {
    applyAddressFromRoute();
  }
);

onBeforeUnmount(() => {
  // keep initialized true during client-side navigation so we don't re-append
  // the initial message when coming back from address selection.
});
</script>

<template>
  <div
    data-testid="chat-view"
    class="md:container md:mx-auto h-full p-4 flex flex-col gap-4"
  >
    <!-- Address documents and info block under the header -->
    <div v-if="selectedAddress" class="w-full bg-base-200 rounded-lg border px-4 py-3">
      <h2 class="font-semibold text-base">
        Dokumente und Informationen für: {{ selectedAddress!.original }}
      </h2>
      <p class="text-sm text-base-content/70 mt-1">
        Gemarkung: {{ selectedAddress!.gemarkung || "–" }}
        <span class="mx-2">|</span>
        Flurstücknummer: {{ selectedAddress!.parcel || "–" }}
      </p>

      <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="font-medium mb-1">Bebauungsplan:</div>
          <div class="flex flex-wrap gap-2">
            <a
              v-if="selectedAddress!.planStatus === 'available' && selectedAddress!.plan"
              :href="selectedAddress!.plan"
              target="_blank"
              rel="noopener"
              class="btn btn-outline btn-sm"
            >
              Bebauungsplan PDF herunterladen
            </a>
            <a
              v-if="selectedAddress!.planStatus === 'available' && selectedAddress!.festsetzungen"
              :href="selectedAddress!.festsetzungen"
              target="_blank"
              rel="noopener"
              class="btn btn-outline btn-sm"
            >
              Festsetzungen PDF herunterladen
            </a>
            <span v-if="selectedAddress!.planStatus !== 'available'" class="text-sm text-base-content/60">
              Keine Bebauungspläne verfügbar
            </span>
          </div>
        </div>

        <div>
          <div class="font-medium mb-1">Landesbauordnung:</div>
          <a
            :href="selectedAddress!.lbo"
            target="_blank"
            rel="noopener"
            class="btn btn-outline btn-sm"
          >
            {{ `${formatLboLabel(selectedAddress!.lbo)} herunterladen` }}
          </a>
        </div>
      </div>
    </div>

    <div class="flex gap-4 flex-1">
      <div class="flex-initial md:w-8/12 flex flex-col overflow-hidden px-4">
      <div class="flex-1 mb-4 overflow-hidden">
        <ChatMessages
          :messages="chatStore.chatHistory"
          :is-loading="chatStore.isLoading"
        />
      </div>
      <ChatInput :is-disabled="chatStore.isLoading" />
      <ChatDisclaimer class="mt-2 mx-1" />
    </div>
      <div class="flex-1 md:w-4/12 overflow-hidden flex flex-col gap-4">
        <ChatDocumentContainer :documents="chatStore.chatDocuments" />
      </div>
    </div>
  </div>
</template>
