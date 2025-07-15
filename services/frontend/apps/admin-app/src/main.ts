import App from './App.vue';
import { i18n } from '@i18n/admin';
import { routes } from './routes';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';

export async function setupApp() {
  const router = createRouter({
    history: createWebHistory("/"),
    routes
  });

  const app = createApp(App).use(i18n).use(createPinia());

  app.use(router);
  await router.isReady();

  app.mount('#app');
  return app;
}
setupApp();
