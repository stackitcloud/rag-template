import App from './App.vue';
import { i18n } from '@i18n/chat';
import { routes } from './routes';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import '@shared/ui';
import { initializeMarkdown } from "@shared/utils";

export async function setupApp() {
  const router = createRouter({
    history: createWebHistory("/"),
    routes
  });

  initializeMarkdown();

  const app = createApp(App).use(i18n).use(createPinia());

  app.use(router);
  await router.isReady();

  app.mount('#app');
  return app;
}
setupApp();
