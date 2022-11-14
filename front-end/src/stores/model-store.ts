import { AxiosError } from 'axios';
import { LocationQueryValue } from 'vue-router';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface Artifact {
  name: string;
  type: string;
  url: string;
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
  inferenceServiceName: string;
  explanation: string;
  usage: string;
  limitations: string;
  markdown: string;
  performance: string;
  artifacts: Artifact[];
}

export interface CreateModelCard {
  title: string;
  task: string;
  summary: string;
  tags: string[];
  frameworks: string[];
  owner?: string;
  pointOfContact?: string;
  inferenceServiceName: string;
  markdown: string;
  performance: string;
  artifacts: Artifact[];
  description: string;
  explanation: string;
  usage: string;
  limitations: string;
}
export interface SearchParams {
  p?: number; // page
  n?: number; // rows per page
  sort?: string;
  desc?: boolean;
  all?: boolean;
  creatorUserId?: string;
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
    ], // TODO: use MongoDB aggregate so only tasks in DB are shown
    frameworks: [
      // TODO: Dynamically get frameworks
      'Keras',
      'PyTorch',
    ],
    tags: [
      'Example',
      'Keras', // TODO: dynamically get tags
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
        return Promise.reject('Failed to create model card');
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
  },
});
