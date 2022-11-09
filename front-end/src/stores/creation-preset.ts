import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export const creationPreset = defineStore('createPreset', {
  state: () => {
    return {
      tasksList: [
        'Computer Vision',
        'Natural Language Processing',
        'Audio Processing',
        'Multimodal',
        'Reinforcement Learning',
        'Tabular',
      ],
      datasetPlatforms: ['', 'ClearML'],
      experimentPlatforms: ['', 'ClearML'],
      markdownToolbar: [
        'undo redo | blocks | fontfamily fontsize | forecolor backcolor | bold italic underline strikethrough |',
        ' alignleft aligncenter alignright | outdent indent | bullist numlist | charmap anchor hr | insertdatetime | link image table | replaceValues',
      ],
    };
  },
  getters: {},
  actions: {},
});
