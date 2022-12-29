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
  baseURL: process.env.backendAPI,
  withCredentials: true,
});

// Set Interceptor

api.interceptors.response.use(
  (response) => {
    // If request succeeds, reset indicator
    Cookies.remove('requestRetry');
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !Cookies.get('requestRetry')) {
      // Set indicator to prevent infinite loop
      Cookies.set('requestRetry', 'true');
      // get refresh token
      const authStore = useAuthStore();
      await authStore.refresh();
      return api(originalRequest);
    }
    return Promise.reject(error);
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
