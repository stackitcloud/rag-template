<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const address = ref('');

function handleSubmit(e: Event) {
  e.preventDefault();
  const q = address.value?.trim();
  if (q) {
    router.push({ name: 'portal-address', query: { q } });
  }
}
</script>

<template>
  <div class="min-h-screen bg-base-100 flex items-center justify-center">
    <div class="max-w-xl w-full bg-base-200 shadow rounded-box p-8">
      <h1 class="text-2xl font-bold mb-4 text-center">
        Informationsportal der Unteren Bauaufsichtsbehörden des Saarlandes
      </h1>
      <p class="opacity-80 mb-6 text-center">
        Geben Sie eine Adresse oder Flurstücknummer ein, um relevante Bauvorschriften und Bebauungspläne abzurufen und Fragen zu stellen.
      </p>
      <form @submit="handleSubmit" class="space-y-4">
        <div>
          <label for="address" class="block text-sm font-medium mb-2">Adresse oder Flurstücknummer eingeben:</label>
          <input
            id="address"
            v-model="address"
            type="text"
            placeholder="z.B. Saarbrücken, Markt 1 oder 1234/567"
            required
            class="input input-bordered w-full"
          />
        </div>
        <button type="submit" class="btn btn-primary w-full">Adresse prüfen</button>
      </form>
    </div>
  </div>
</template>
