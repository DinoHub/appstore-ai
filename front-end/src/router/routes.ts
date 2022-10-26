import CreateModel from 'pages/CreateModel.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import { RouteRecordRaw } from 'vue-router';
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => MainLayout,
    children: [{ path: '', component: () => LoginPage }],
  },
  {
    path: '/models',
    component: () => MainLayout,
    children: [
      {
        path: 'create',
        component: () => CreateModel,
      },
    ],
  },
  {
    path: '/',
    component: () => MainLayout,
    children: [{ path: '', component: () => DashboardPage }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => ErrorNotFound,
  },
];

export default routes;
