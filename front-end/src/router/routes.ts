import CreateModel from 'pages/CreateModel.vue';
import DashboardLayout from 'layouts/DashboardLayout.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import ModelPage from 'pages/ModelPage.vue';
import { RouteRecordRaw } from 'vue-router';
import SearchLayout from 'layouts/SearchLayout.vue';
import SearchModelsPage from 'pages/SearchModelsPage.vue';
import { useAuthStore } from 'src/stores/auth-store';
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: MainLayout,
    children: [{ path: '', name: 'Login', component: LoginPage }],
    beforeEnter: (to) => {
      const auth = useAuthStore();
      if (auth.access_token) {
        // Logged in
        return '/';
      }
    },
  },
  {
    path: '/model',
    component: MainLayout,
    name: 'Model',
    children: [
      {
        path: '',
        component: SearchModelsPage,
        beforeEnter: () => {
          // Redirect to search page filtered by user
          return {
            name: 'Models',
          };
        },
      },
      {
        path: ':userId',
        component: SearchModelsPage,
        beforeEnter: (to) => {
          // Redirect to search page filtered by user
          return {
            name: 'Models',
            query: {
              creator: to.params.userId,
            },
          };
        },
      },
      {
        path: ':userId/:modelId',
        component: ModelPage,
      },
      {
        path: 'create',
        name: 'Create Model',
        component: CreateModel,
      },
    ],
  },
  {
    path: '/models',
    component: SearchLayout,
    children: [
      {
        path: '',
        name: 'Models',
        component: SearchModelsPage,
      },
      {
        path: ':userId',
        component: SearchModelsPage,
        beforeEnter: (to) => {
          // Redirect to search page filtered by user
          return {
            name: 'Models',
            query: {
              creator: to.params.userId,
            },
          };
        },
      },
    ],
  },
  {
    path: '/',
    component: DashboardLayout,
    children: [{ path: '', name: 'Dashboard', component: DashboardPage }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: ErrorNotFound,
  },
];

export default routes;
