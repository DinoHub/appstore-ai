import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface Config {
  [key: string]: string;
}

export interface Experiment {
  id: string;
  name: string;
  project_name: string;
  tags: string[];
  frameworks: string[];
  config: Config;
  owner: string;
}
export const useExpStore = defineStore('exp', {
  state: () => ({}),
  getters: {},
  actions: {
    async getExperimentByID(exp_id: string): Promise<Experiment> {
      try {
        const res = await api.get(`experiments/${exp_id}`, {
          params: {
            connector: 'clearml',
            return_plots: false,
            return_artifacts: false,
            is_admin: false,
          },
        });
        const data: Experiment = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Experiment Not Found');
          this.router.push('/404');
        }
        return Promise.reject('Unable to get experiment');
      }
    },
  },
});
