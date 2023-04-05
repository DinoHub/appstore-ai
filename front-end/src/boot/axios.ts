import axios, { AxiosInstance } from 'axios';
import { Notify } from 'quasar';
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
  baseURL: process.env.API,
  withCredentials: true,
});
// Set Interceptor

api.interceptors.response.use(
  (response) => {
    // If request succeeds, reset indicator
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401) {
      const authStore = useAuthStore();

      await authStore.refresh();
      return api(originalRequest);
    }
    if (error.response?.status === 403) {
      const authStore = useAuthStore();
      Notify.create({
        type: 'warning',
        message: 'This account does not have sufficient privileges',
      });
      return authStore.logout();
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
