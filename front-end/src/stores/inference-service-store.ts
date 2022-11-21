import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface InferenceEngineService {
  serviceName: string;
  modelId: string;
  ownerId: string;
  imageUri: string;
  inferenceUrl: string;
  containerPort?: number;
}

export interface InferenceServiceStatus {
  conditions: {
    lastTransitionTime: string;
    status: string;
    type: string;
  }[];
  url: string;
}

export const useInferenceServiceStore = defineStore('service', {
  state: () => ({}),
  getters: {},
  actions: {
    async getServiceReady(
      serviceName: string,
      maxRetries = 1,
      backoffSeconds = 10,
    ): Promise<boolean> {
      try {
        for (let noRetries = 0; noRetries < maxRetries; noRetries++) {
          let ready = true;
          const res = await api.get(`engines/${serviceName}/status`);
          const data: InferenceServiceStatus = res.data;
          console.log(data);
          for (const status of data.conditions) {
            if (status.status !== 'True') {
              ready = false;
            }
          }
          if (ready) {
            return true;
          }
          // Sleep for backoffSeconds
          await new Promise((r) => setTimeout(r, 1000 * backoffSeconds));
        }
        return false;
      } catch (error) {
        return Promise.reject(false);
      }
    },
    async getServiceByName(
      serviceName: string,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.get(`engines/${serviceName}`);
        const data: InferenceEngineService = res.data;
        return data;
      } catch (error) {
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.error('Inference Engine Not Found');
        }
        return Promise.reject('Unable to get inference engine');
      }
    },
    async createService(
      modelId: string,
      imageUri: string,
      port?: number,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.post('/engines/', {
          modelId: modelId,
          imageUri: imageUri,
          port: port,
        });
        const data: InferenceEngineService = res.data;
        return data;
      } catch (error) {
        return Promise.reject('Unable to create inference engine');
      }
    },
    async updateService(
      serviceName: string,
      imageUri?: string,
      port?: number,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.patch(`/engines/${serviceName}`, {
          imageUri: imageUri,
          port: port,
        });
        const data: InferenceEngineService = res.data;
        return data;
      } catch (error) {
        return Promise.reject('Unable to update inference engine');
      }
    },
    async deleteService(serviceName: string): Promise<void> {
      try {
        await api.delete(`/engines/${serviceName}`);
      } catch (error) {
        return Promise.reject('Unable to delete inference engine');
      }
    },
  },
});
