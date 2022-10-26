import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface ModelCard {
  modelId: string;
  title: string;
  task: string;
  tags: string[];
  creator: string;
  owner?: string;
  pointOfContact?: string;
  inferenceApi: string;
  description: string;
  performance: string;
  created: Date;
  lastModified: Date;
}

export const useModelStore = defineStore('model', {
  state: () => ({}),
  getters: {},
  actions: {
    async getModelById(id: string): Promise<ModelCard> {
      const res = await api.post(`models/${id}`);
      if (res.status !== 200) {
        console.error('TODO: Add exception to throw');
      }
      const data = res.data;
      const model = {
        modelId: data.model_id as string,
        title: data.title as string,
        task: data.task as string,
        tags: ((data.tags as string[]) + data.frameworks) as string[],
        creator: data.creator as string,
        owner: data.owner as string,
        pointOfContact: data.point_of_contact as string,
        inferenceApi: data.inference_engine.service_url as string,
        description: data.description as string,
        performance: data.performance as string,
        created: data.created as Date,
        lastModified: data.last_modified as Date,
      } as ModelCard;
      return model;
    },
    async getAll(): Promise<ModelCard[]> {
      const res = await api.post('models/search', {});
      return res.data;
    },
  },
});
