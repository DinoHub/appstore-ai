import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { Artifact } from 'src/stores/model-store';

export interface Dataset {
  id: string;
  name: string;
  tags: string[];
  project?: string;
  created?: string;
  files?: string[];
  artifacts?: Artifact[];
  default_remote?: string;
}

export const useDatasetStore = defineStore('dataset', {
  state: () => ({
    datasetConnectors: [
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

  getters: {},

  actions: {
    async getDatasetById(
      datasetId: string,
      connector: string,
    ): Promise<Dataset> {
      try {
        const res = await api.get(`datasets/${datasetId}`, {
          params: {
            connector: connector,
          },
        });
        const data: Dataset = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Dataset Not Found');
          Notify.create({
            message: `${connector} Dataset with ID: ${datasetId} not found`,
            color: 'negative',
          });
        } else {
          Notify.create({
            message: `Error getting ${connector} Dataset with ID: ${datasetId}`,
            color: 'negative',
          });
        }
        throw error;
      }
    },
  },
});
