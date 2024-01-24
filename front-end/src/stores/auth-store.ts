import jwt_decode from 'jwt-decode';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';
import KeyCloakService from 'src/security/KeycloakService';

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

export const useAuthStore = defineStore('auth', {
  state: () => ({
    _user: null as User | null,
    _accessToken: undefined as string | undefined,
    _returnUrl: null as string | null,
  }),
  actions: {
    async getToken() {
      // When calling RefreshToken() function, check if token is updated first before keeping it in our state.
      const isTokenUpdated = await KeyCloakService.CallRefreshToken();
      if (isTokenUpdated) {
        const access_token = KeyCloakService.GetAccessToken();
        this._accessToken = access_token
      }
      return this._accessToken
    },
    /**
     * Login to the application 
     * @param userId  User ID
     * @param password Plain text password
     */
    async login() {
      const isAuthenticated = await KeyCloakService.CallLogin();
      if (isAuthenticated) {
        const role_list: string[] | undefined= KeyCloakService.GetUserRoles()
        this._user = {
          userId: KeyCloakService.GetUserId(), 
          name: KeyCloakService.GetFullName(), 
          role: role_list[0]
          // role: "admin" //TODO: remove hardcode when doing authorization aspect
        } as User;
      } else {
        this._user = null;
      }

      if (this._returnUrl?.startsWith('/admin')) {
        if (this._user?.role != 'admin') {
          Notify.create({
            type: 'negative',
            message:
              'Failed to login, insufficient privileges'
          });
          this.logout()
        }
      }
      this.router.push(this._returnUrl || '/');
    },
    // TODO: change to camelCase
    /**
     * Login to admin panel
     * @param userId User ID of admin user
     * @param password Plain text password
     */
    async admin_login(userId: string, password: string): Promise<void> {
      try {
        const creds = new FormData();
        creds.append('username', userId);
        creds.append('password', password);
        const response = await api.post('/keycloak_auth/', creds);
        // Validate admin, if not admin, error will be thrown
        await api.get('/auth/is_admin');
        // Decode JWT
        const { access_token }: LoginResponse = response.data;
        const jwt_data = jwt_decode(access_token) as JWT;
        if (!jwt_data) {
          console.error('Failed to decode');
          throw new Error('Failed to decode');
        }

        localStorage.removeItem('creationStore');
        this.user = {
          // TODO: Replace with actual api call
          userId: jwt_data.sub,
          name: jwt_data.name,
          role: jwt_data.role,
        } as User;
        this.router.push('/admin');
      } catch (err) {
        this.admin_logout();
        Notify.create({
          type: 'negative',
          message:
            'Failed to login, credentials invalid or insufficient privileges',
        });
        return Promise.reject(err);
      }
    },
    /**
     * Logout of the application
     */
    logout(): void {
      KeyCloakService.CallLogOut();
      this._user = null;
    },
    /**
     * Use refresh token to get new access token
     */
    async refresh(): Promise<void> {
      console.warn('Refreshing access token');
      try {
        await KeyCloakService.CallRefreshToken();
      } catch (err) {
        this.logout();
      }
    },
  },

  getters: {
    user: (state) => state._user,
    returnUrl: (state) => state._returnUrl,
    accessToken: (state) => state._accessToken,
  },

  persist: {
    // add returnURL path back if you fix this
    storage: localStorage,
    paths: ['user'],
  },
});
