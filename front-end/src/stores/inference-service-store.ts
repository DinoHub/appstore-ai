import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';

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
  ready: boolean;
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
          const res = await api.get(`engines/${serviceName}/status`);
          const data: InferenceServiceStatus = res.data;

          if (data.ready) {
            console.log('Service is ready');
            return true;
          }
          // exponential backoff algo to wait for service to be ready
          // Sleep for backoffSeconds
          const backoffSeconds =
            Math.pow(2, noRetries) + Math.random() + initialWaitSeconds;
          console.warn(
            `Service not yet ready. Backing off for ${backoffSeconds} seconds (${noRetries}/${maxRetries})`,
          );
          if (backoffSeconds > maxDeadlineSeconds) {
            console.error('Service not ready, max retries exceeded');
            console.error(data);
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
        // TODO: Ability to set resource limits starving
        // the cluster of resources
        // see wip/set-knative-resource-limits branch
        // which has partial implementation
        const serviceData: Record<string, any> = {
          modelId: modelId,
          imageUri: imageUri,
          env: env,
        };
        if (port) {
          // NOTE: currently frontend has tmp disabled
          // the ability to set port, assume port is always 8080
          // this is because backend code for Emissary
          // does not yet support creating new Listener for
          // that port
          serviceData.containerPort = port;
        }

        const res = await api.post('/engines/', serviceData);
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
      // wait for a few seconds first to give time for the service to be created
      await new Promise((r) => setTimeout(r, 1000 * 5));
      const ready = await this.getServiceReady(serviceName);
      if (ready) {
        return { serviceName, inferenceUrl };
      } else {
        Notify.create({
          message: 'Failed to create service',
          color: 'negative',
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
