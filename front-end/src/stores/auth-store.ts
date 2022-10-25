import { defineStore } from 'pinia';
import { Ref, ref } from 'vue';

// export const useAuthStore = defineStore({
//   id: 'auth',
//   state: () => ({
//     user: true, // tmp
//     returnUrl: null,
//   }),
//   actions: {},
// });

export const useAuthStore = defineStore('auth', () => {
  const user = ref(true);
  const returnUrl: Ref<null | string> = ref(null);
})
