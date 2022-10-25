import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import jwt_decode from 'jwt-decode'

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
  token_type: string; // bearer
}

export interface JWT {
  sub: string; // userId
  name: string;
  role: Role;
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') ?? '{}') as User | null,
    returnUrl: null as string | null,
    token: null as string | null,
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
        const data: LoginResponse = response.data;
        const jwt_data = jwt_decode(data.access_token) as JWT

        if (!jwt_data) {
          console.error('Failed to decode');
        }
        this.user = {
          // TODO: Replace with actual api call
          userId: jwt_data.sub,
          name: jwt_data.name,
          role: jwt_data.role,
        } as User;

        // Set JWT token
        this.token = data.access_token;
      } catch (err) {
        console.error(err);
      }
      localStorage.setItem('user', JSON.stringify(this.user));
      this.router.push(this.returnUrl || '/');
    },
    logout(): void {
      this.user = null;
      this.token = null;
      localStorage.removeItem('user');
      this.router.push('/login');
    },
  },
});
