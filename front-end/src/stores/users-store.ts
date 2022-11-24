import { AxiosError } from 'axios';
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
  total_rows: number;
}

export const useUsersStore = defineStore('users', {
  state: () => ({}),
  actions: {
    async getUsersPaginated(
      pageNumber: number,
      userNumber: number,
      nameSearch: string,
      privilegeSearch: number,
      sortBy: string,
      descending: boolean
    ): Promise<UsersPaginated> {
      try {
        if (typeof sortBy != 'string') {
          sortBy = 'lastModified';
          descending = true;
        }
        const res = await api.post(`iam/?desc=${descending}&sort=${sortBy}`, {
          page_num: pageNumber,
          user_num: userNumber,
          name: nameSearch,
          admin_priv: privilegeSearch,
        });
        const { results, total_rows }: UsersPaginated = res.data;
        return { results, total_rows };
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
    async createUser(
      name: string,
      adminPriv: string,
      password: string,
      confirmPassword: string
    ): Promise<void> {
      try {
        if (
          name.trim() == '' ||
          adminPriv.toLowerCase() != 'admin' ||
          adminPriv.toLowerCase() != 'user' ||
          password.trim() == '' ||
          confirmPassword.trim() == ''
        ) {
          Notify.create({
            type: 'error',
            position: 'top',
            message: `Fill in all required fields`,
          });
        } else {
          let priv;
          if (adminPriv.toLowerCase() == 'admin') {
            priv = true;
          } else {
            priv = false;
          }
          const res = await api.post('iam/add', {
            user_id: '',
            name: name,
            password: password,
            password_confirm: confirmPassword,
            admin_priv: priv,
          });
          console.log(res.headers);
          Notify.create({
            type: 'positive',
            position: 'top',
            message: `Successfully created user`,
          });
        }
      } catch (err) {
        Notify.create({
          message: `Error occurred while creating user`,
          color: 'error',
          position: 'top',
          icon: 'error',
        });
      }
    },
  },
});
