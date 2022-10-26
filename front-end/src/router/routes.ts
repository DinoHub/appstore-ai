import CreateModel from 'pages/CreateModel.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import ModelPage from 'pages/ModelPage.vue';
import { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: MainLayout,
    children: [{ path: '', component: LoginPage }],
    beforeEnter: (to) => {
      const auth = useAuthStore();
      if (auth.access_token) {
        // Logged in
        return '/';
      }
    },
  },
  {
    path: '/models',
    component: MainLayout,
    children: [
      {
        path: ':id',
        component: ModelPage,
      },
      {
        path: 'create',
        component: CreateModel,
      },
    ],
  },
  {
    path: '/',
    component: MainLayout,
    children: [{ path: '', component: DashboardPage }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: ErrorNotFound,
  },
];

export default routes;
