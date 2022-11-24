import { AxiosError } from 'axios';
import { Chart } from 'src/components/models';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface CreateUser {
  name: string;
  adminPriv: string;
  password: string;
  confirm_password: string;
}

export interface Users {
  userId: string;
  name: string;
  adminPriv: any;
  created: string;
  lastModified: string;
}

export interface UsersPaginated {
  results: Users[];
  total: number;
}

export const useUsersStore = defineStore('users', {
  state: () => ({}),
  actions: {
    async getUsersPaginated(
      pageNumber: number,
      userNumber: number,
      nameSearch: string,
      privilegeSearch: number
    ): Promise<UsersPaginated> {
      try {
        const res = await api.post(`iam/`, {
          page_num: pageNumber,
          user_num: userNumber,
          name: nameSearch,
          admin_priv: privilegeSearch,
        });
        const { results, total }: UsersPaginated = res.data;
        return { results, total };
      } catch (error) {
        const errRes = error as AxiosError;
        Notify.create({
          message: `Error occurred while retrieving users`,
          color: 'error',
          icon: 'error',
        });
        return Promise.reject('Unable to query for users');
      }
    },
  },
});
