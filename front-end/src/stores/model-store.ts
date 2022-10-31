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

export interface SearchResponse {
  results: ModelCardSummary[];
  total: number;
}

export const useModelStore = defineStore('model', {
  state: () => ({}),
  getters: {},
  actions: {
    async getModels(params: SearchParams): Promise<SearchResponse> {
      try {
        const res = await api.get('models/', {
          params: {
            ...params,
            return: [
              'modelId',
              'creatorUserId',
              'title',
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
    async getModelsByUser(userId: string): Promise<SearchResponse> {
      try {
        const res = await api.get(`/models/${userId}`, {
          params: {
            return: [
              'modelId',
              'creatorUserId',
              'title',
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
        return Promise.reject(error);
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
