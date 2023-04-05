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
  status: 'Running' | 'Failed' | 'Pending' | 'Unknown' | 'Succeeded';
  serviceName: string;
  ready: boolean;
  schedulable: boolean;
  expectedReplicas: number;
  message?: string;
}

export const imageUriRegex = new RegExp(
  '^(?:(?=[^:/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?::(?![.-])[a-zA-Z0-9_.-]{1,128})?$',
);

export const useInferenceServiceStore = defineStore('service', {
  state: () => ({
    previewServiceName: null as string | null,
    currentServiceStatus: null as InferenceServiceStatus | null,
  }),
  getters: {},
  actions: {
    /**
     * Use the Kubernetes API to check if the service is ready
     * by pinging the back-end to get the status of the service
     * @param serviceName Name of the service to check
     * @param maxRetries Maximum number of retries to check
     * @param initialWaitSeconds Initial wait time in seconds
     * @param maxDeadlineSeconds Maximum time to wait in seconds
     * @returns
     */
    async getServiceReady(
      serviceName: string,
      maxRetries = 15,
      initialWaitSeconds = 10,
      maxDeadlineSeconds = 300, // 5 minutes
    ): Promise<InferenceServiceStatus> {
      try {
        for (let noRetries = 0; noRetries < maxRetries; noRetries++) {
          const res = await api.get(`engines/${serviceName}/status`);
          const data: InferenceServiceStatus = res.data;
          this.currentServiceStatus = data; // Store to allow other components to access
          console.log(data);
          if (data.expectedReplicas === 0) {
            console.warn('Service has no replicas');
            return data;
          }
          // if unschedulable, don't keep waiting, return to inform user
          if (!data.schedulable) {
            console.warn('Service is not schedulable');
            return data;
          }
          if (data.ready) {
            console.log('Service is ready');
            return data;
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
            return data;
          }
          await new Promise((r) => setTimeout(r, 1000 * backoffSeconds));
        }
        return Promise.reject('Unable to get status of service');
      } catch (error) {
        // find out if its a 404
        const errRes = error as AxiosError;
        if (errRes.response?.status === 404) {
          console.warn('Inference Engine Not Found');
          return Promise.reject(404);
        }
        console.error(error);
        return Promise.reject('Unable to get status of service');
      }
    },
    /**
     * Get the service by name
     * @param serviceName Name of the service to get
     * @returns Service data
     */
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
    /**
     * Create a new service
     * NOTE: Currently back-end does not support different ports
     * so you should always pass in 8080 (til we fix this)
     * @param modelId Model ID to create service for
     * @param imageUri Image URI to use for service
     * @param numGpus Number of GPUs to use for service
     * @param port Port number to use for service
     * @param env A mapping of environment variables and their values
     * @returns Promise of the service data
     */
    async createService(
      modelId: string,
      imageUri: string,
      numGpus: number,
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
          numGpus: numGpus,
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
    /**
     * Create a temporary service meant for testing.
     * @param modelId Model ID to create service for
     * @param imageUri Image URI to use for service
     * @param numGpus Number of GPUs to use for service
     * @param port Port number to use for service
     * @param env Mapping of environment variables and their values
     * @returns The service name, inference URL, and status
     */
    async launchPreviewService(
      modelId: string,
      imageUri: string,
      numGpus: number,
      port?: number,
      env?: Record<string, any>,
    ): Promise<{
      serviceName: string;
      inferenceUrl: string;
      status: InferenceServiceStatus;
    }> {
      Notify.create({
        message: 'Creating service, please wait...',
      });
      const { serviceName, inferenceUrl } = await this.createService(
        modelId,
        imageUri,
        numGpus,
        port,
        env,
      );
      // store service name so we can delete it later
      this.previewServiceName = serviceName;
      // wait for a few seconds first to give time for the service to be created
      await new Promise((r) => setTimeout(r, 1000 * 5));
      const status = await this.getServiceReady(serviceName);
      if (status.ready) {
        return { serviceName, inferenceUrl, status };
      } else {
        Notify.create({
          message: 'Failed to create service. Error: ' + status.message,
          color: 'negative',
        });
        await this.deleteService(serviceName); // Cleanup
        return Promise.reject('Failed to launch preview service');
      }
    },
    /**
     * Update an existing service
     * @param serviceName ID of the service to update
     * @param imageUri Image URI to use for service
     * @param numGpus Number of GPUs to use for service
     * @param port Port number to use for service
     * @param env Mapping of environment variables and their values
     * @returns Promise of the service data
     */
    async updateService(
      serviceName: string,
      imageUri?: string,
      numGpus?: number,
      port?: number,
      env?: Record<string, any>,
    ): Promise<InferenceEngineService> {
      try {
        const res = await api.patch(`/engines/${serviceName}`, {
          imageUri: imageUri,
          port: port,
          env: env,
          numGpus: numGpus,
        });
        const data: InferenceEngineService = res.data;
        return data;
      } catch (error) {
        return Promise.reject('Unable to update inference engine');
      }
    },
    /**
     * Deletes an existing service
     * @param serviceName ID of the service to delete
     * @returns Promise that resolves when the service is deleted
     */
    async deleteService(serviceName: string): Promise<void> {
      try {
        await api.delete(`/engines/${serviceName}`);
      } catch (error) {
        return Promise.reject('Unable to delete inference engine');
      }
    },
    /**
     * Attempt to scale a service to a given number of replicas
     * @param serviceName ID of the service to scale
     * @param replicas Value to scale the service to
     * @returns Promise that resolves when the service is scaled
     */
    async scaleService(serviceName: string, replicas: number): Promise<void> {
      try {
        await api.patch(`/engines/${serviceName}/scale/${replicas}`, {});
      } catch (error) {
        Notify.create({
          message: 'Failed to scale service. Error: ' + error,
          color: 'negative',
        });
        return Promise.reject('Unable to scale inference engine');
      }
    },
    /**
     * Repairs a service, recreating any missing resources (e.g deployment, service, etc.)
     * @param serviceName ID of the service to restore
     * @returns Promise that resolves when the service is restored
     */
    async restoreService(serviceName: string): Promise<void> {
      try {
        await api.post(`/engines/${serviceName}/restore`, {});
      } catch (error) {
        Notify.create({
          message: 'Failed to restore service. Error: ' + error,
          color: 'negative',
        });
        return Promise.reject('Unable to restore inference engine');
      }
    },
  },
});
