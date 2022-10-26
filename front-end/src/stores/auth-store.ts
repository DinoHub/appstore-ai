import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import jwt_decode from 'jwt-decode';

export enum Role {
  user = 'user',
  admin = 'admin',
}
export interface User {
  userId: string | null;
  name: string | null;
  role: Role;
}

export interface LoginResponse {
  access_token: string; // JWT
  refresh_token: string;
  token_type: string; // bearer
}

export interface JWT {
  sub: string; // userId
  name: string;
  role: Role;
}

// TODO: Fix storing the access token in a secured way that Axios can use for the OAuth
// currently have to store accesstoken in Cookie that is not secured (httponly)
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') ?? '{}') as User | null,
    returnUrl: null as string | null,
    access_token: null as string | null,
    refresh_token: null as string | null,
  }),
  actions: {
    async login(userId: string, password: string): Promise<void> {
      try {
        const creds = new FormData();
        creds.append('username', userId);
        creds.append('password', password);
        const response = await api.post('/auth', creds);
        if (response.status !== 200) {
          console.error('Failed');
        }
        // Decode JWT
        const { access_token, refresh_token }: LoginResponse = response.data;
        const jwt_data = jwt_decode(access_token) as JWT;

        if (!jwt_data) {
          console.error('Failed to decode');
        }
        this.user = {
          // TODO: Replace with actual api call
          userId: jwt_data.sub,
          name: jwt_data.name,
          role: jwt_data.role,
        } as User;
        this.access_token = access_token;
        this.refresh_token = refresh_token;
      } catch (err) {
        console.error(err);
      }
      localStorage.setItem('user', JSON.stringify(this.user));
      this.router.push(this.returnUrl || '/');
    },
    logout(): void {
      this.user = null;
      localStorage.removeItem('user');
      this.router.push('/login');
    },
    async refresh(): Promise<void> {
      console.warn('Refreshing access token');
      try {
        const response = await api.post('/auth/refresh', {
          grant_type: 'refresh_token',
          refresh_token: this.refresh_token,
        });

        if (response.status !== 200) {
          console.error('Failed to refresh access token');
          this.logout();
        }
        const { access_token }: LoginResponse = response.data;
        // Set tokens
        this.access_token = access_token;
      } catch (err) {
        console.error(err);
      }
    },
  },
  persist: true,
});
