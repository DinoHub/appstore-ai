import { Chart } from 'src/components/models';
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
    markdownContent: '' as string,
    performanceMarkdown: '' as string,
    plots: [] as Chart[],
  }),
  getters: {},
  actions: {
    async loadFromMetadata(modelId: string): Promise<void> {
      // Get User ID
      const authStore = useAuthStore();
      const modelStore = useModelStore();

      const original_data = await modelStore.getModelById(
        authStore.user?.userId ?? '',
        modelId,
      );

      // Load the data
      this.tags = original_data.tags;
      this.frameworks = original_data.frameworks;
      // TODO: what to do with modelPath?
      this.experimentPlatform = original_data.experiment?.connector ?? '';
      this.experimentID = original_data.experiment?.experimentId ?? '';
      this.datasetPlatform = original_data.dataset?.connector ?? '';
      this.datasetID = original_data.dataset?.datasetId ?? '';

      this.modelName = original_data.title;
      this.modelTask = original_data.task;
      this.modelOwner = original_data.owner ?? '';
      this.modelPOC = original_data.pointOfContact ?? '';
      this.modelDesc = original_data.description;
      this.modelExplain = original_data.explanation;
      this.modelUsage = original_data.usage;
      this.modelLimitations = original_data.limitations;

      this.markdownContent = original_data.markdown;
      this.performanceMarkdown = original_data.performance;

      // Look through artifacts to find model
      // TODO: Replace modelPath with something less hard-coded
      for (const artifact of original_data.artifacts) {
        if (artifact.artifactType === 'model') {
          this.modelPath = artifact.url;
          break;
        }
      }
    },
    async checkMetadataValues() {
      const keys = Object.keys(this.$state).filter(
        (item) =>
          ![
            'step',
            'tags',
            'frameworks',
            'performanceMarkdown',
            'markdownContent',
            'datasetID',
            'experimentID',
            'datasetPlatform',
            'experimentPlatform',
            'modelOwner',
            'modelPOC',
          ].includes(item),
      );
      if (this.$state.tags.length == 0 || this.$state.frameworks.length == 0) {
        return false;
      }
      if (
        (this.$state.datasetID == '' && this.$state.datasetPlatform != '') ||
        (this.$state.experimentID == '' && this.$state.experimentPlatform != '')
      ) {
        return false;
      }
      for (const key of keys) {
        if (this.$state[key] == '') {
          console.log(this.$state);
          return false;
        }
      }
      return true;
    },
    async submitEdit(modelId: string) {
      const authStore = useAuthStore();
      const modelStore = useModelStore();

      modelStore.updateModel(
        {
          title: this.modelName,
          task: this.modelTask,
          tags: this.tags,
          frameworks: this.frameworks,
          description: this.modelDesc,
          explanation: this.modelExplain,
          usage: this.modelUsage,
          limitations: this.modelLimitations,
          markdown: this.markdownContent,
          performance: this.performanceMarkdown,
          experiment: {
            connector: this.experimentPlatform,
            experimentId: this.experimentID,
          },
          dataset: {
            connector: this.datasetPlatform,
            datasetId: this.datasetID,
          },
          artifacts: [
            {
              artifactType: 'model',
              url: this.modelPath,
              name: 'Model',
              timestamp: new Date().toISOString(),
            },
          ],
          owner: this.modelOwner,
          pointOfContact: this.modelPOC,
        },
        authStore.user?.userId ?? '',
        modelId,
      );
    },
  },
});
