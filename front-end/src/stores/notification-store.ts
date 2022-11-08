import { QNotifyOptions } from 'quasar';
import { defineStore } from 'pinia';

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as QNotifyOptions[],
  }),

  getters: {
  },

  actions: {
  }
});
