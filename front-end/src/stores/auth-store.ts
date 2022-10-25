import { defineStore } from 'pinia';

export const useAuthStore = defineStore({
  id : 'auth'
}, {
  state: () => ({
    user: true, // tmp
    returnUrl: null
  }),
  actions: {
    
  }
});
