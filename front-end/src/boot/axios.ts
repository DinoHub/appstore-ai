import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

import { Cookies } from 'quasar';
import { boot } from 'quasar/wrappers';
import { useAuthStore } from 'src/stores/auth-store';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL: 'http://localhost:8080',
  withCredentials: true,
});

// Set Interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    config.headers['Authorization'] = `Bearer ${authStore.access_token}`;
    return config
  }
)

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 403 && !originalRequest._retry) {
      alert("Hi")
      originalRequest._retry = true;
      // get refresh token
      const authStore = useAuthStore();
      await authStore.refresh();
      return api(originalRequest);
    }
  }
);

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
});

export { api };
