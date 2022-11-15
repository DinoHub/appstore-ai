import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { useModelStore } from './model-store';

export const useEditMetadataStore = defineStore('editMetadata', {
  state: () => ({
    step: 1 as number,
    tags: [] as string[],
    frameworks: [] as string[],
    modelPath: '' as string,
    experimentPlatform: '' as string, // todo: enum
    experimentID: '' as string,
    datasetPlatform: '' as string,
    datasetID: '' as string,
    modelName: '' as string,
    modelTask: '' as string,
    modelOwner: '' as string,
    modelPOC: '' as string,
    modelDesc: '' as string,
    modelExplain: '' as string,
    modelUsage: '' as string,
    modelLimitations: '' as string,
    inferenceImage: '' as string,
    markdownContent: '' as string,
    performanceMarkdown: '' as string,
  }),
  getters: {},
  actions: {
    async loadFromMetadata(modelId: string) {
      // Get User ID
      const authStore = useAuthStore();
      const modelStore = useModelStore();

      const original_data = await modelStore.getModelById(
        authStore.user?.userId ?? '',
        modelId,
      );

      return;
    },
  },
});
