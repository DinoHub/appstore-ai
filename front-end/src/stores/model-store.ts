import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface ModelCard {
  modelId: string;
  title: string;
  task: string;
  tags: string[];
  frameworks: string[];
  creator: string;
  owner?: string;
  pointOfContact?: string;
  inferenceApi: string;
  description: string;
  performance: string;
  created: string;
  lastModified: string;
}

export const useModelStore = defineStore('model', {
  state: () => ({}),
  getters: {},
  actions: {
    async getModelById(userId: string, modelId: string): Promise<ModelCard> {
      try {
        const res = await api.get(`models/${userId}/${modelId}`);
        const data = res.data;
        const model = {
          modelId: data.model_id as string,
          title: data.title as string,
          task: data.task as string,
          tags: data.tags as string[],
          frameworks: data.frameworks as string[],
          creator: data.creatorUserId as string,
          owner: data.owner as string,
          pointOfContact: data.pointOfContact as string,
          inferenceApi: data.inferenceApi as string,
          description: data.description as string,
          performance: data.performance as string,
          created: data.created as string,
          lastModified: data.lastModified as string,
        } as ModelCard;
        return model;
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
      } catch (error) {
        console.error(error);
      }
    },
  },
});
