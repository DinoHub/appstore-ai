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
