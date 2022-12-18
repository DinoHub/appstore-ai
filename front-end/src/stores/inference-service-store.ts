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
  resourceLimits: {
    cpu_cores: number;
    memory_gb: number;
  };
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
  state: () => ({
    cpuCoreOptions: [
      { label: '0.5', value: 0.5 },
      { label: '1', value: 1 },
      { label: '2', value: 2 },
      { label: '4', value: 4 },
      { label: '8', value: 8 },
      { label: '16', value: 16 },
    ],
    memoryOptions: [
      { label: '1GB', value: 1 },
      { label: '2GB', value: 2 },
      { label: '4GB', value: 4 },
      { label: '8GB', value: 8 },
      { label: '16GB', value: 16 },
      { label: '32GB', value: 32 },
    ],
  }),
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
      containerCPUCores: number,
      containerMemoryGB: number,
      port?: number,
      env?: Record<string, any>,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.post('/engines/', {
          modelId: modelId,
          imageUri: imageUri,
          port: port,
          env: env,
          resourceLimits: {
            cpu_cores: containerCPUCores,
            memory_gb: containerMemoryGB,
          },
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
      containerCPUCores: number,
      containerMemoryGB: number,
      port?: number,
      env?: Record<string, any>,
    ) {
      Notify.create({
        message: 'Creating service, please wait...',
      });
      const { serviceName, inferenceUrl } = await this.createService(
        modelId,
        imageUri,
        containerCPUCores,
        containerMemoryGB,
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
      containerCPUCores?: number,
      containerMemoryGB?: number,
      port?: number,
      env?: Record<string, any>,
    ): Promise<InferenceEngineService> {
      try {
        // set resourceLimits to undefined if not provided
        // else, make a dictionary with non-undefined values
        let resourceLimits: Record<string, number> | undefined = {};

        if (containerCPUCores !== undefined) {
          resourceLimits['cpu_cores'] = containerCPUCores;
        }
        if (containerMemoryGB !== undefined) {
          resourceLimits['memory_gb'] = containerMemoryGB;
        }
        if (Object.keys(resourceLimits).length === 0) {
          resourceLimits = undefined;
        }
        const res = await api.patch(`/engines/${serviceName}`, {
          imageUri: imageUri,
          port: port,
          env: env,
          resourceLimits: resourceLimits,
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
