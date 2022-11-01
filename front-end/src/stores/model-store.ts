import { AxiosError } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

enum ArtifactTypes {
  model = 'model',
  dataset = 'dataset',
}
export interface Artifact {
  name: string;
  type: ArtifactTypes;
  url: string;
}
export interface ModelCard extends ModelCardSummary {
  owner?: string;
  pointOfContact?: string;
  inferenceApi: string;
  description: string;
  performance: string;
  artifacts: Artifact[];
}

export interface ModelCardSummary {
  modelId: string;
  creatorUserId: string;
  title: string;
  task: string;
  summary: string;
  tags: string[];
  frameworks: string[];
  lastModified: string;
  created: string;
}

export interface SearchParams {
  p?: number; // page
  n?: number; // rows per page
  sort?: string;
  desc?: boolean;
  all?: boolean;
  creatorUserId?: string;
  title?: string;
  tags?: string[];
  frameworks?: string[];
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
              'summary',
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
