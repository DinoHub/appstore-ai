import { Chart } from 'src/components/models';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { useExperimentStore } from './experiment-store';
import { Artifact, useModelStore } from './model-store';
import { useDatasetStore } from './dataset-store';
import { useAccessControlStore } from './access-control-store';
import { Notify } from 'quasar';

export const useEditMetadataStore = defineStore('editMetadata', {
  state: () => ({
    step: 1 as number,
    artifacts: [] as Artifact[],
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
    modelOwnerUsername: '' as string,
    modelPOC: '' as string,
    modelAccessList: [] as string[],
    enableModelAccess: false as boolean,
    previousModelAccessList: [] as string[],
    modelDesc: '' as string,
    modelExplain: '' as string,
    modelUsage: '' as string,
    modelLimitations: '' as string,
    markdownContent: '' as string,
    performanceMarkdown: '' as string,
    plots: [] as Chart[],
  }),
  getters: {
    mainModelArtifact(): Artifact {
      return {
        name: 'Model',
        artifactType: 'mainModel',
        url: this.modelPath,
      };
    },
    /**
     * Checks if model card is missing any required fields
     * @returns True if all metadata is valid
     */
    metadataValid(): boolean {
      const keys = Object.keys(this).filter(
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
            'plots',
            'artifacts',
            'previousModelAccessList',
            'enableModelAccess',
            'modelAccessList',
            'metadataValid'
          ].includes(item)
      );
      if (this.tags.length == 0 || this.frameworks.length == 0) {
        return false;
      }
      if (
        (this.datasetID == '' && this.datasetPlatform != '') ||
        (this.experimentID == '' && this.experimentPlatform != '') ||
        (this.modelAccessList.length == 0 && this.enableModelAccess == true)
      ) {
        return false;
      }
      for (const key of keys) {
        if (this[key] == '') {
          console.log(this);
          console.log(key);
          return false;
        }
      }
      return true;
    },
  },
  actions: {
    /**
     * Attempt to populate the store with data from the experiment
     * @returns Promise that resolves when data is loaded
     */
    async loadMetadataFromExperiment(): Promise<void> {
      if (!this.experimentID || !this.experimentPlatform) {
        return Promise.reject();
      }
      const experimentStore = useExperimentStore();
      try {
        const metadata = await experimentStore.getExperimentByID(
          this.experimentID,
          this.experimentPlatform,
          false, // returnPlots
          true // returnArtifacts
        );
        this.tags = Array.from(new Set([...this.tags, ...metadata.tags]));
        this.frameworks = Array.from(
          new Set([...this.frameworks, ...metadata.frameworks])
        );
        this.artifacts = Array.from(
          new Set([
            ...this.artifacts,
            ...Object.values(metadata.artifacts ?? {}),
          ])
        );
      } catch (error) {
        return Promise.reject(error);
      }
    },
    async loadMetadataFromDataset(): Promise<void> {
      if (!this.datasetID || !this.datasetPlatform) {
        return Promise.reject();
      }
      const datasetStore = useDatasetStore();
      try {
        const metadata = await datasetStore.getDatasetById(
          this.datasetID,
          this.datasetPlatform
        );
        this.tags = Array.from(new Set([...this.tags, ...metadata.tags]));
        this.artifacts = Array.from(
          new Set([...this.artifacts, ...(metadata.artifacts ?? [])])
        );
      } catch (error) {
        return Promise.reject(error);
      }
    },

    /**
     * Based on a list of usernames provided from frontend, do a check 
     * against Keycloak to see if they exist.
     * @returns {Promise<void>} A promise that resolves when check is done
     */
    async validateUsernames(editor: string): Promise<void> {
      const AccessControlStore = useAccessControlStore();
      const authStore = useAuthStore();
      const user = authStore.user?.userId ?? undefined

      // Remove items from previousModelAccessList that are not in modelAccessList
      // With this, when username that was removed before and added again, we can validate it against keycloak
      this.previousModelAccessList = this.previousModelAccessList.filter(value => this.modelAccessList.includes(value));
  
      // Split the input in modelAccessList by , or space or ; 
      this.modelAccessList = this.modelAccessList
        .flatMap(username => username.split(/[,;\s]+/))
        .filter(Boolean); // remove empty strings

      // Remove duplicates here if frontend did not remove, by converting array to set and to array.
      // Why? q-select cannot prevent duplicates if user copied a string of usernames in which some already exist in the box.
      this.modelAccessList = [...new Set(this.modelAccessList)]
      
      // If model owner entered his/her own username in the list, remove it and trigger notification.
      if (user && this.modelAccessList.includes(user) && editor == 'modelowner') {
        this.modelAccessList.splice(this.modelAccessList.indexOf(user), 1);
        Notify.create({
            message: `The username, ${user} is the model's owner and already has access.`,
            type: 'negative',
            timeout: 5000
        });
      }

      // If admin added model owner's username in the list using /admin, remove it and trigger notification.
      if (this.modelOwnerUsername && this.modelAccessList.includes(this.modelOwnerUsername) && editor == 'admin') {
        this.modelAccessList.splice(this.modelAccessList.indexOf(this.modelOwnerUsername), 1);
        Notify.create({
          message: `The username, ${this.modelOwnerUsername} is the model's owner and already has access.`,
          type: 'negative',
          timeout: 5000
        });
      }
      
      // If admin entered his/her own username in the list in /admin, remove it and trigger notification.
      if (user && this.modelAccessList.includes(user) && editor == 'admin') {
        this.modelAccessList.splice(this.modelAccessList.indexOf(user), 1);
        Notify.create({
            message: `The username, ${user} is the admin and already has access.`,
            type: 'negative',
            timeout: 5000
        });
      }
      
      // filter out newly added usernames to validate against Keycloak instead of checking the whole list
      const addedUsernames = this.modelAccessList.filter(value => !this.previousModelAccessList.includes(value));

      if (addedUsernames.length > 0){
        const validationResults = await AccessControlStore.validateUsernamesWithKeycloak(addedUsernames)
        this.previousModelAccessList.push(...validationResults.newUsernamesList)
        this.modelAccessList = this.previousModelAccessList
      }
      
    },

    /**
     * Populate the store with data from existing model card
     * @param modelId Model ID to load metadata from
     * @param userId Associated user ID that created said model
     */
    async loadFromMetadata(modelId: string, userId: string): Promise<void> {
      // Get User ID
      const authStore = useAuthStore();
      const modelStore = useModelStore();

      const original_data = await modelStore.getModelById(userId, modelId);

      // Load the data
      this.tags = original_data.tags;
      this.frameworks = original_data.frameworks;
      this.experimentPlatform = original_data.experiment?.connector ?? '';
      this.experimentID = original_data.experiment?.experimentId ?? '';
      this.datasetPlatform = original_data.dataset?.connector ?? '';
      this.datasetID = original_data.dataset?.datasetId ?? '';

      this.modelName = original_data.title;
      this.modelTask = original_data.task;
      this.modelOwner = original_data.owner ?? '';
      this.modelOwnerUsername = original_data.creatorUserId ?? '';
      this.modelPOC = original_data.pointOfContact ?? '';
      this.modelAccessList = original_data.accessControl.authorized;
      this.enableModelAccess = original_data.accessControl.enabled;
      this.modelDesc = original_data.description;
      this.modelExplain = original_data.explanation;
      this.modelUsage = original_data.usage;
      this.modelLimitations = original_data.limitations;

      this.markdownContent = original_data.markdown;
      this.performanceMarkdown = original_data.performance;

      // Look through artifacts to find model
      // TODO: Replace modelPath with something less hard-coded
      for (const artifact of original_data.artifacts) {
        if (artifact.artifactType === 'mainModel') {
          this.modelPath = artifact.url;
          break;
        }
      }
    },
    /**
     * Submit the metadata to the backend
     * @param modelId ID of the model to update
     * @param userId associated ID of creator of said model
     */
    async submitEdit(modelId: string, userId: string): Promise<void> {
      const authStore = useAuthStore();
      const modelStore = useModelStore();
      if (authStore.user?.name) {
        if (this.modelOwner == '') {
          this.modelOwner = authStore.user.name;
        }
        if (this.modelPOC == '') {
          this.modelPOC = authStore.user.name;
        }
      }
      if (this.enableModelAccess == false) {
        this.modelAccessList = [];
      }
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
            outputUrl: '',
          },
          dataset: {
            connector: this.datasetPlatform,
            datasetId: this.datasetID,
          },
          artifacts: Array.from(
            new Set([this.mainModelArtifact, ...this.artifacts])
          ),
          owner: this.modelOwner,
          pointOfContact: this.modelPOC,
          accessControl: {
            enabled: this.enableModelAccess,
            authorized: this.modelAccessList
          }
        },
        userId,
        modelId
      );
    },
  },
});
