import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface ModelCard {
  id: string;
}

export const useModelStore = defineStore('model', {
  state: () => ({
    models: [],
  }),
  getters: {
    userModels(state) {
      return state.models;
    },
  },
  actions: {
    getModelById(id: string): ModelCard {
      return {
        id: id,
      } as ModelCard;
    },
    async getAll(): Promise<ModelCard[]> {
      const res = await api.post('models/search', {});
      return res.data
    },
  },
});
