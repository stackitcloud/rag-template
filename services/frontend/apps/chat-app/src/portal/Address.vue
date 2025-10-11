<script setup lang="ts">
import { searchAddresses, type AddressData } from '@shared/portal-address';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const query = ref<string>('');
const matches = ref<AddressData[]>([]);

const hasNoMatches = computed(() => matches.value.length === 0);
const hasOneMatch = computed(() => matches.value.length === 1);

function runSearch(q: string) {
  query.value = q;
  matches.value = q ? searchAddresses(q) : [];
}

function selectAddress(addr: string) {
  router.push({ name: 'chat', query: { addr } });
}

onMounted(() => {
  const q = (route.query.q as string) || '';
  runSearch(q);
});

watch(
  () => route.query.q,
  (newQ: unknown) => runSearch((newQ as string) || '')
);

watch(
  () => matches.value,
  (vals: AddressData[]) => {
    if (vals.length === 1) {
      selectAddress(vals[0].original);
    }
  }
);
</script>

<template>
  <div class="min-h-screen bg-base-100 py-8">
    <div class="max-w-2xl mx-auto bg-base-200 shadow rounded-box p-8">
      <template v-if="hasNoMatches">
        <p class="text-error mb-4">Keine passende Adresse gefunden für "{{ query }}". Bitte überprüfen Sie die Eingabe oder versuchen Sie eine andere Adresse.</p>
        <RouterLink :to="{ name: 'portal-home' }" class="link link-primary">Zurück zur Suche</RouterLink>
      </template>
      <template v-else-if="hasOneMatch">
        <p>Weiterleitung…</p>
      </template>
      <template v-else>
        <h1 class="text-2xl font-bold mb-4">Mögliche Adressen oder Flurstücke für: {{ query }}</h1>
        <p class="opacity-80 mb-6">Wählen Sie die passende Adresse aus, um die relevanten Dokumente und den Chatbot zu öffnen.</p>
        <ul class="space-y-2 mb-6">
          <li v-for="m in matches" :key="m.original">
            <button @click="selectAddress(m.original)" class="btn btn-outline btn-primary w-full justify-start">
              {{ m.original }}
            </button>
          </li>
        </ul>
        <RouterLink :to="{ name: 'portal-home' }" class="link link-primary">Zurück zur Suche</RouterLink>
      </template>
    </div>
  </div>

</template>
