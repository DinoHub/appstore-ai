import CreateModel from 'src/pages/ModelCreate.vue';
import DashboardLayout from 'layouts/DashboardLayout.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import ModelInferenceServiceEdit from 'src/pages/ModelInferenceServiceEdit.vue';
import ModelMetadataEdit from 'pages/ModelMetadataEdit.vue';
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
      if (auth.user?.userId) {
        // Logged in
        return '/';
      }
    },
  },
  {
    path: '/model',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Model',
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
        path: ':userId/:modelId/edit',
        beforeEnter: (to) => {
          const auth = useAuthStore();
          if (auth.user?.userId !== to.params.userId) {
            // Check if user is the owner of the model
            return '/';
          }
        },
        children: [
          {
            path: '',
            name: 'Edit',
            redirect: 'metadata',
          },
          {
            path: 'metadata',
            name: 'Model Metadata',
            component: ModelMetadataEdit,
          },
          {
            path: 'inference',
            name: 'Model Inference Service',
            component: ModelInferenceServiceEdit,
          },
        ],
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
