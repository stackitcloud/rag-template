import { ChatView } from '@chat';
import type { RouteRecordRaw } from 'vue-router';
import Home from './portal/Home.vue';
import Address from './portal/Address.vue';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'portal-home',
    component: Home,
  },
  {
    path: '/address',
    name: 'portal-address',
    component: Address,
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
    props: true,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () => {
      return `/`;
    }
  }
];
