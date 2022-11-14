import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export const useCreationPreset = defineStore('createPreset', {
  state: () => {
    return {
      tasksList: [
        'Computer Vision',
        'Natural Language Processing',
        'Audio Processing',
        'Multimodal',
        'Reinforcement Learning',
        'Tabular',
      ] as string[],
      datasetPlatforms: ['', 'ClearML'] as string[],
      experimentPlatforms: ['', 'ClearML'] as string[],
    };
  },
  getters: {},
  actions: {},
});
