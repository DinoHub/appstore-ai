import { AxiosError } from 'axios';
import { Chart } from 'src/components/models';
import { Notify } from 'quasar';
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
  scalars?: Chart[];
  plots?: Chart[];
}

export const useExperimentStore = defineStore('experiment', {
  state: () => ({
    experimentConnectors: [
      {
        label: 'None',
        value: '',
      },
      {
        label: 'ClearML',
        value: 'clearml',
      },
    ] as Record<string, string>[],
  }),
  actions: {
    async getExperimentByID(
      experimentId: string,
      connector: string,
      returnPlots = false,
      returnArtifacts = false,
    ): Promise<Experiment> {
      try {
        const res = await api.get(`experiments/${experimentId}`, {
          params: {
            connector: connector,
            return_plots: returnPlots,
            return_artifacts: returnArtifacts,
          },
        });
        const data: Experiment = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Experiment Not Found');
          Notify.create({
            message: `${connector} Experiment with ID: ${experimentId} not found`,
            color: 'error',
          });
        } else {
          Notify.create({
            message: 'Failed to get experiment due to server error',
            color: 'error',
          });
        }
        return Promise.reject('Unable to get experiment');
      }
    },
  },
});
