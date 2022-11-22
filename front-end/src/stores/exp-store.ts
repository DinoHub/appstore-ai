import { AxiosError } from 'axios';
import { Chart } from 'src/components/models';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';
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
  scalars?: Chart[];
  plots?: Chart[];
}

export const useExpStore = defineStore('exp', {
  state: () => ({
    experimentConnectors: ['', 'ClearML'] as string[],
  }),
  getters: {},
  actions: {
    async getExperimentByID(
      exp_id: string,
      returnPlots = false,
      returnArtifacts = false,
    ): Promise<Experiment> {
      try {
        const res = await api.get(`experiments/${exp_id}`, {
          params: {
            connector: 'clearml',
            return_plots: returnPlots,
            return_artifacts: returnArtifacts,
          },
        });
        const data: Experiment = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        console.error(errRes.response?.data);
        if (errRes.response?.status === 404) {
          console.error('Experiment Not Found');
          // TODO: Notify reject
        }
        return Promise.reject('Unable to get experiment');
      }
    },
  },
});
