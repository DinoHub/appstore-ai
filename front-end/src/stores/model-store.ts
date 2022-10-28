import { AxiosError } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface ModelCard extends ModelCardSummary {
  owner?: string;
  pointOfContact?: string;
  inferenceApi: string;
  description: string;
  performance: string;
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

export const useModelStore = defineStore('model', {
  state: () => ({}),
  getters: {},
  actions: {
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
    async getModelsByUser(userId: string): Promise<ModelCardSummary[]> {
      try {
        const res = await api.post('/models/search', {
          creatorUserId: userId,
          returnAttrs: [
            'modelId',
            'creatorUserId',
            'title',
            'summary',
            'tags',
            'frameworks',
            'lastModified',
            'created',
          ],
        });
        const data: ModelCard[] = res.data;
        return data;
      } catch (error) {
        return Promise.reject(error);
      }
    },
  },
});
