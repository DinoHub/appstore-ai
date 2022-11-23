import { defineStore } from 'pinia';

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

  actions: {},
});
