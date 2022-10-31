import CreateModel from 'pages/CreateModel.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import ModelPage from 'pages/ModelPage.vue';
import { RouteRecordRaw } from 'vue-router';
import SearchModelsPage from 'pages/SearchModelsPage.vue';
import { useAuthStore } from 'src/stores/auth-store';
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
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
        path: '',
        name: 'search',
        component: SearchModelsPage,
      },
      {
        path: ':userId/:modelId',
        component: ModelPage,
      },
      {
        path: 'create',
        name: 'createModel',
        component: CreateModel,
      },
    ],
  },
  {
    path: '/',
    component: MainLayout,
    name: 'dashboard',
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
