import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { LocationQueryValue } from 'vue-router';
import { Notify } from 'quasar';

export interface Artifact {
  name: string;
  artifactType: string;
  url: string;
  timestamp?: string;
}

export interface LinkedExperiment {
  connector: string;
  experimentId: string;
}

export interface LinkedDataset {
  connector: string;
  datasetId: string;
}

export interface ModelCardSummary {
  modelId: string;
  creatorUserId: string;
  title: string;
  task: string;
  description: string;
  tags: string[];
  frameworks: string[];
  lastModified: string;
  created: string;
}

export interface ModelCard extends ModelCardSummary {
  owner?: string;
  pointOfContact?: string;
  inferenceServiceName?: string;
  videoLocation?: string;
  explanation: string;
  usage: string;
  limitations: string;
  markdown: string;
  performance: string;
  artifacts: Artifact[];
  experiment?: LinkedExperiment;
  dataset?: LinkedDataset;
}

export interface CreateModelCard {
  title: string;
  task: string;
  tags: string[];
  frameworks: string[];
  owner?: string;
  pointOfContact?: string;
  inferenceServiceName?: string;
  videoLocation?: string;
  markdown: string;
  performance: string;
  artifacts: Artifact[];
  description: string;
  explanation: string;
  usage: string;
  limitations: string;
  experiment?: LinkedExperiment;
  dataset?: LinkedDataset;
}

export interface UpdateModelCard {
  title?: string;
  task?: string;
  tags?: string[];
  frameworks?: string[];
  owner?: string;
  pointOfContact?: string;
  inferenceServiceName?: string;
  videoLocation?: string;
  markdown?: string;
  performance?: string;
  artifacts?: Artifact[];
  description?: string;
  explanation?: string;
  usage?: string;
  limitations?: string;
  experiment?: LinkedExperiment;
  dataset?: LinkedDataset;
}

export interface SearchParams {
  p?: number; // page
  n?: number; // rows per page
  sort?: string;
  desc?: boolean;
  all?: boolean;
  creatorUserId?: string;
  creatorUserIdPartial?: string;
  title?: string;
  tags?: string[] | LocationQueryValue[];
  frameworks?: string[] | LocationQueryValue[];
  tasks?: string[] | LocationQueryValue[];
}

export interface AvailableFilterResponse {
  tags: string[];
  frameworks: string[];
  tasks: string[];
}

export interface SearchResponse {
  results: ModelCardSummary[];
  total: number;
}

export const useModelStore = defineStore('model', {
  state: () => ({
    tasks: [
      'Computer Vision',
      'Natural Language Processing',
      'Audio Processing',
      'Multimodal',
      'Reinforcement Learning',
      'Tabular',
    ],
  }),
  getters: {},
  actions: {
    async getFilterOptions(): Promise<AvailableFilterResponse> {
      try {
        const res = await api.get('models/_db/options/filters');
        return res.data as AvailableFilterResponse;
      } catch (error) {
        return Promise.reject(error);
      }
    },
    async getModels(params: SearchParams): Promise<SearchResponse> {
      try {
        const res = await api.get('models/', {
          params: {
            ...params,
            return: [
              'modelId',
              'creatorUserId',
              'title',
              'task',
              'description',
              'tags',
              'frameworks',
              'lastModified',
              'created',
            ],
          },
        });
        const { results, total }: SearchResponse = res.data;
        return { results, total };
      } catch (error) {
        const errRes = error as AxiosError;
        console.error('Error', errRes.message);
        return Promise.reject(error);
      }
    },
    async createModel(metadata: CreateModelCard): Promise<ModelCard> {
      try {
        const res = await api.post('models/', metadata);
        const data: ModelCard = res.data;
        return data;
      } catch (error) {
        if (error.response.status == 409) {
          Notify.create({
            type: 'warning',
            message:
              'The model name already exists under you. Please enter a different one.',
            position: 'top-right',
          });
          return Promise.reject(
            'The model name already exists under you. Please enter a different one.'
          );
        } else {
          Notify.create({
            message: 'Failed to create model',
            type: 'negative',
            position: 'top-right',
          });
          return Promise.reject('Failed to create model card');
        }
      }
    },
    async createModelVideo(metadata: CreateModelCard): Promise<ModelCard> {
      try {
        const res = await api.post('models/', metadata);
        const data: ModelCard = res.data;
        return data;
      } catch (error) {
        if (error.response.status == 409) {
          Notify.create({
            type: 'warning',
            message:
              'The model name already exists under you. Please enter a different one.',
            position: 'top-right',
          });
          return Promise.reject(
            'The model name already exists under you. Please enter a different one.'
          );
        } else {
          Notify.create({
            message: 'Failed to create model',
            type: 'negative',
            position: 'top-right',
          });
          return Promise.reject('Failed to create model card');
        }
      }
    },
    async updateModel(
      metadata: UpdateModelCard,
      userId: string,
      modelId: string
    ): Promise<void> {
      try {
        console.warn(metadata);
        await api.put(`models/${userId}/${modelId}`, metadata);
      } catch (error) {
        const errRes = error as AxiosError;
        console.error(errRes.response?.data);
        return Promise.reject('Failed to edit model card');
      }
    },
    async getModelById(userId: string, modelId: string): Promise<ModelCard> {
      try {
        const res = await api.get(`models/${userId}/${modelId}`);
        const data: ModelCard = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Model Card Not Found');
          this.router.push('/404');
        }
        return Promise.reject('Unable to get model metadata');
      }
    },
    async deleteModelById(userId: string, modelId: string): Promise<void> {
      try {
        await api.delete(`models/${userId}/${modelId}`);
        this.router.push('/');
        Notify.create({
          message: `Model ${userId}/${modelId} has been deleted!`,
          type: 'negative',
        });
      } catch (error) {
        console.error(error);
      }
    },
    async deleteModelMultiple(models: Array<any>): Promise<void> {
      try {
        console.log(models);
        // const compositeKeys = [];
        // for (const element of models) {
        //   compositeKeys.push({
        //     model_id: element.modelId,
        //     creator_user_id: element.creatorUserId,
        //   });
        // }
        const removeModels = models.map(({ modelId, creatorUserId }) => {
          return { model_id: modelId, creator_user_id: creatorUserId };
        });
        console.log(removeModels);

        await api.delete(`models/multi`, {
          data: { card_package: removeModels },
        });
        Notify.create({
          message: `Models have been deleted!`,
          type: 'positive',
        });
      } catch (error) {
        console.error(error);
      }
    },
  },
});
