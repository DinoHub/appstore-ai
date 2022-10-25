import { defineStore } from 'pinia';
import { reactive, Ref, ref } from 'vue';
import router from '../router/index';

// export const useAuthStore = defineStore({
//   id: 'auth',
//   state: () => ({
//     user: true, // tmp
//     returnUrl: null,
//   }),
//   actions: {},
// });

export interface User {
  userId: string | null;
  name: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') ?? '{}') as User | null,
  }),
  actions: {
    login() {
      this.user = {
        userId: 'tmp1',
        name: 'Tmp User',
      };
      localStorage.setItem('user', JSON.stringify(this.user));
    },
    logout() {
      this.user = null;
      localStorage.removeItem('user');
      this.router.push('/login');
    },
  },
});
