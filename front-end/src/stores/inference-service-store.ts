import { Store, defineStore } from 'pinia';

import { AxiosError } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';

export interface InferenceEngineService {
  serviceName: string;
  modelId: string;
  ownerId: string;
  imageUri: string;
  inferenceUrl: string;
  containerPort?: number;
  env?: Record<string, any>;
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
      maxRetries = 10,
      initialWaitSeconds = 10,
      maxDeadlineSeconds = 300,
    ): Promise<boolean> {
      try {
        for (let noRetries = 0; noRetries < maxRetries; noRetries++) {
          let ready = true;
          const res = await api.get(`engines/${serviceName}/status`);
          const data: InferenceServiceStatus = res.data;
          for (const status of data.conditions) {
            if (status.status !== 'True') {
              ready = false;
            }
          }
          if (ready) {
            return true;
          }
          // Sleep for backoffSeconds
          const backoffSeconds =
            Math.pow(2, noRetries) + Math.random() + initialWaitSeconds;
          console.warn(`Backing off for ${backoffSeconds} seconds`);
          if (backoffSeconds > maxDeadlineSeconds) {
            return false;
          }
          await new Promise((r) => setTimeout(r, 1000 * backoffSeconds));
        }
        return false;
      } catch (error) {
        return Promise.reject('Unable to get status of KNative service');
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
          console.warn('Inference Engine Not Found');
        }
        return Promise.reject('Unable to get inference engine');
      }
    },
    async createService(
      modelId: string,
      imageUri: string,
      port?: number,
      env?: Record<string, any>,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.post('/engines/', {
          modelId: modelId,
          imageUri: imageUri,
          port: port,
          env: env,
        });
        const data: InferenceEngineService = res.data;
        return data;
      } catch (error) {
        return Promise.reject('Unable to create inference engine');
      }
    },
    async launchPreviewService(
      modelId: string,
      imageUri: string,
      port?: number,
      env?: Record<string, any>,
    ) {
      Notify.create({
        message: 'Creating service, please wait...',
      });
      const { serviceName, inferenceUrl } = await this.createService(
        modelId,
        imageUri,
        port,
        env,
      );
      const ready = await this.getServiceReady(serviceName);
      if (ready) {
        return { serviceName, inferenceUrl };
      } else {
        Notify.create({
          message: 'Failed to create service',
          color: 'error',
        });
        await this.deleteService(serviceName); // Cleanup
        return Promise.reject('Failed to launch preview service');
      }
    },
    async updateService(
      serviceName: string,
      imageUri?: string,
      port?: number,
      env?: Record<string, any>,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.patch(`/engines/${serviceName}`, {
          imageUri: imageUri,
          port: port,
          env: env,
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
