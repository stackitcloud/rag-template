import { DocumentView } from '@admin';
import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'documents',
    component: DocumentView
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  },
];
