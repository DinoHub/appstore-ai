import { defineStore } from 'pinia';

export interface User {
  userId: string | null;
  name: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') ?? '{}') as User | null,
    returnUrl: null as string | null
  }),
  actions: {
    async login(userId: string, password: string): Promise<void> {
      this.user = { // TODO: Replace with actual api call
        userId: 'tmp1',
        name: 'Tmp User',
      };
      localStorage.setItem('user', JSON.stringify(this.user));
      this.router.push(this.returnUrl || '/');
    },
    logout(): void {
      this.user = null;
      localStorage.removeItem('user');
      this.router.push('/login');
    },
  },
});
