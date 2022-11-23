import CreateModel from 'pages/CreateModel.vue';
import DashboardLayout from 'layouts/DashboardLayout.vue';
import DashboardPage from 'pages/DashboardPage.vue';
import AdminDashboardPage from 'pages/AdminDashboardPage.vue';
import ErrorNotFound from 'pages/ErrorNotFound.vue';
import AdminLoginPage from 'pages/AdminLoginPage.vue';
import LoginPage from 'pages/LoginPage.vue';
import MainLayout from 'layouts/MainLayout.vue';
import AdminDashboardLayout from 'layouts/AdminDashboardLayout.vue';
import ModelMetadataEdit from 'pages/ModelMetadataEdit.vue';
import ModelInferenceServiceEdit from 'src/pages/ModelInferenceServiceEdit.vue';
import ModelPage from 'pages/ModelPage.vue';
import { RouteRecordRaw } from 'vue-router';
import SearchLayout from 'layouts/SearchLayout.vue';
import SearchModelsPage from 'pages/SearchModelsPage.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { Notify } from 'quasar';
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Login',
        component: LoginPage,
        beforeEnter: (to) => {
          const auth = useAuthStore();
          if (auth.user?.userId) {
            // Logged in
            return '/';
          }
        },
      },
      {
        path: 'admin',
        name: 'Admin',
        beforeEnter: (to) => {
          const auth = useAuthStore();
          if (auth.user?.role == 'admin') {
            // Logged in
            return '/admin';
          }
        },
        component: AdminLoginPage,
      },
    ],
  },
  {
    path: '/admin',
    component: AdminDashboardLayout,
    children: [
      {
        path: '',
        name: 'Admin Dashboard',
        component: AdminDashboardPage,
        beforeEnter: (to) => {
          const auth = useAuthStore();
          if (auth.user?.role != 'admin') {
            auth.logout();
            Notify.create({
              type: 'warning',
              position: 'top',
              message: 'This account does not have sufficient privileges',
            });
            return '/login/admin';
          }
        },
      },
    ],
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
