import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';

export interface CreateUser {
  name: string;
  adminPriv: string;
  password: string;
  confirm_password: string;
}

export interface Users {
  userId: string;
  name: string;
  adminPriv: 'admin' | 'user';
  created: string;
  lastModified: string;
}

export interface UsersPaginated {
  results: Users[];
  total_rows: number;
}

export const useUsersStore = defineStore('users', {
  state: () => ({
    privilegeOptions: [
      { value: 2, label: 'All' },
      {
        value: 1,
        label: 'Admin',
      },
      {
        value: 0,
        label: 'User',
      },
    ],
    privilege: { value: 2, label: 'All' },
    createdDateRange: null as null,
    lastModifiedRange: null as null,
    nameSearch: '' as string,
    idSearch: '' as string,
  }),
  actions: {
    /**
     * Retrives users in a paginated format
     * @param pageNumber Page number to retrieve
     * @param userNumber Number of users per page
     * @param sortBy What field to sort by
     * @param descending If the sort should be descending instead of ascending
     * @returns Promise that resolves to the list of users and the total number of users
     */
    async getUsersPaginated(
      pageNumber: number,
      userNumber: number,
      sortBy: string,
      descending: boolean
    ): Promise<UsersPaginated> {
      try {
        let desc;
        let sort;
        if (typeof sortBy != 'string') {
          desc = '';
          sort = '';
        } else {
          desc = `?desc=${descending}`;
          sort = `&sort=${sortBy}`;
        }
        let tempModifiedRange = { from: '', to: '' };
        let tempCreatedDateRange = { from: '', to: '' };
        if (
          typeof this.lastModifiedRange == 'object' &&
          this.lastModifiedRange != null
        ) {
          tempModifiedRange = Object.create(this.lastModifiedRange);
          tempModifiedRange.from = tempModifiedRange.from.replaceAll('/', '-');
          tempModifiedRange.to = tempModifiedRange.to.replaceAll('/', '-');
          tempModifiedRange.to = `${tempModifiedRange.to} 24:00:00`;
        }
        if (
          typeof this.lastModifiedRange == 'string' &&
          this.lastModifiedRange != null
        ) {
          tempModifiedRange = { from: '', to: '' };
          tempModifiedRange.from = this.lastModifiedRange.replaceAll('/', '-');
          tempModifiedRange.to = this.lastModifiedRange.replaceAll('/', '-');
          tempModifiedRange.to = `${tempModifiedRange.to} 24:00:00`;
        }
        if (
          typeof this.createdDateRange == 'object' &&
          this.createdDateRange != null
        ) {
          tempCreatedDateRange = Object.create(this.createdDateRange);
          tempCreatedDateRange.from = tempCreatedDateRange.from.replaceAll(
            '/',
            '-'
          );
          tempCreatedDateRange.to = tempCreatedDateRange.to.replaceAll(
            '/',
            '-'
          );
          tempCreatedDateRange.to = `${tempCreatedDateRange.to} 24:00:00`;
        }
        if (
          typeof this.createdDateRange == 'string' &&
          this.createdDateRange != null
        ) {
          tempCreatedDateRange = { from: '', to: '' };
          tempCreatedDateRange.from = this.createdDateRange.replaceAll(
            '/',
            '-'
          );
          tempCreatedDateRange.to = this.createdDateRange.replaceAll('/', '-');
          tempCreatedDateRange.to = `${tempCreatedDateRange.to} 24:00:00`;
        }

        const res = await api.post(`iam/${desc}${sort}`, {
          page_num: pageNumber,
          user_num: userNumber,
          name: this.nameSearch,
          userId: this.idSearch,
          admin_priv: this.privilege.value,
          last_modified_range: tempModifiedRange,
          date_created_range: tempCreatedDateRange,
        });
        const { results, total_rows }: UsersPaginated = res.data;
        return { results, total_rows };
      } catch (error) {
        const errRes = error as AxiosError;
        Notify.create({
          message:
            'Error occurred while retrieving users. Ensure values have been input correctly.',
          color: 'negative',
          icon: 'error',
        });
        console.error(errRes.response?.data);
        return Promise.reject('Unable to query for users');
      }
    },
    async removeUsers(userList: Array<any>): Promise<void> {
      try {
        const removeUsers = userList.map((a) => a.userId);
        await api.delete('iam/delete', {
          data: { users: removeUsers },
        });
        Notify.create({
          type: 'positive',
          message: `${removeUsers.length} user(s) have been removed from database`,
        });
      } catch (err) {
        console.log(err);
        Notify.create({
          message:
            'Error occurred while removing user(s). Ensure values have been input correctly.',
          type: 'negative',
        });
      }
    },
    async editUsersMulti(userList: Array<any>, privilege: any): Promise<void> {
      try {
        const editUsersMulti = userList.map((a) => a.userId);
        await api.put('iam/edit/multi', {
          users: editUsersMulti,
          priv: privilege.value,
        });
        Notify.create({
          type: 'positive',
          message: `${editUsersMulti.length} users edit request completed successfully`,
        });
      } catch (err) {
        console.log(err);
        Notify.create({
          message:
            'Error occurred while send request to edit users. Ensure values have been input correctly.',
          type: 'negative',
        });
      }
    },
    async editUser(
      userId: string,
      name: string,
      adminPriv: string,
      password: string,
      confirmPassword: string
    ): Promise<void> {
      try {
        let priv;
        if (adminPriv.toLowerCase() == 'admin') {
          priv = true;
        } else {
          priv = false;
        }
        await api.put('iam/edit', {
          user_id: userId,
          name: name,
          password: password,
          password_confirm: confirmPassword,
          admin_priv: priv,
        });
        Notify.create({
          type: 'positive',
          message: 'Successfully edited user',
        });
      } catch (err) {
        Notify.create({
          message:
            'Error occurred while editing user. Ensure values have been input correctly.',
          type: 'negative',
        });
      }
    },
    async createUser(
      userId: string,
      name: string,
      adminPriv: string,
      password: string,
      confirmPassword: string
    ): Promise<void> {
      try {
        let priv;
        if (adminPriv.toLowerCase() == 'admin') {
          priv = true;
        } else {
          priv = false;
        }
        await api.post('iam/add', {
          user_id: userId.trim(),
          name: name,
          password: password,
          password_confirm: confirmPassword,
          admin_priv: priv,
        });
        Notify.create({
          type: 'positive',
          message: 'Successfully created user',
        });
      } catch (err) {
        if (err.response.status == 409) {
          Notify.create({
            type: 'warning',
            message: 'The user ID already exists. Please enter a new one.',
          });
          throw new Error();
        } else {
          Notify.create({
            message:
              'Error occurred while creating user. Ensure values have been input correctly.',
            color: 'negative',
            icon: 'error',
          });
          throw new Error();
        }
      }
    },
  },
});
