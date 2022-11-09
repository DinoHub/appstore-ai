import { defineStore } from 'pinia';

export enum Severity {
  default = 'default',
  info = 'info',
  warning = 'warning',
  danger = 'danger',
}
export interface Notification {
  message: string;
  severity: Severity;
}

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [] as Notification[],
  }),

  getters: {},

  actions: {},
});
