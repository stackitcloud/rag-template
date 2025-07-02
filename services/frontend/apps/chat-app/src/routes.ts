import { ChatView } from '@chat';
import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'chat',
    component: ChatView,
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () => {
      return `/`;
    }
  }
];
