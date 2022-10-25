import { defineStore } from 'pinia';
import { reactive, Ref, ref } from 'vue';

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

export const useAuthStore = defineStore('auth', () => {
  const user: User | null = reactive(JSON.parse(localStorage.getItem('user') ?? '{}'));
  const returnUrl: Ref<null | string> = ref(null);

  return {
    user,
    returnUrl,
  };
});
