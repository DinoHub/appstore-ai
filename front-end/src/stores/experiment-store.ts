import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { Chart } from 'src/components/models';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';
import { Artifact } from './model-store';

export interface Config {
  [key: string]: string;
}

export interface Experiment {
  id: string;
  output_url: string;
  name: string;
  project_name: string;
  tags: string[];
  frameworks: string[];
  config: Config;
  owner: string;
  scalars?: Chart[];
  plots?: Chart[];
  artifacts?: Record<string, Artifact>;
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
    /**
     * Retrieves experiment data
     * @param experimentId ID of experiment to get
     * @param connector Experiment connector to use
     * @param returnPlots Whether to return plots or not
     * @param returnArtifacts Whether to return artifacts or not
     * @returns Experiment data
     */
    async getExperimentByID(
      experimentId: string,
      connector: string,
      returnPlots = false,
      returnArtifacts = false
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
        const connecterValue = this.experimentConnectors.find(
          (o) => o.value == connector
        );
        Notify.create({
          message: `${connecterValue.label} Experiment with ID: ${experimentId} found!`,
          type: 'positive',
        });
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Experiment Not Found');
          const connecterValue = this.experimentConnectors.find(
            (o) => o.value == connector
          );
          Notify.create({
            message: `${connecterValue.label} Experiment with ID: ${experimentId} not found`,
            type: 'negative',
          });
        } else {
          Notify.create({
            message: 'Failed to get experiment due to server error',
            type: 'negative',
          });
        }
        return Promise.reject('Unable to get experiment');
      }
    },
  },
});
