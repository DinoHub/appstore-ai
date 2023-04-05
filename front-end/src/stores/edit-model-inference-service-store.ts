import { defineStore } from 'pinia';
import { EnvField } from 'src/components/models';
import { useAuthStore } from './auth-store';
import {
  InferenceServiceStatus,
  useInferenceServiceStore,
} from './inference-service-store';
import { useModelStore } from './model-store';

export const useEditInferenceServiceStore = defineStore(
  'editInferenceService',
  {
    state: () => ({
      step: 1 as number,
      imageUri: '' as string,
      numGpus: 0 as number,
      containerPort: undefined as number | undefined,
      env: [] as EnvField[],
      serviceName: '' as string,
      previewServiceName: null as string | null,
      previewServiceUrl: null as string | null,
      previewServiceStatus: null as InferenceServiceStatus | null,
    }),
    getters: {
      /**
       * Returns true if all metadata is valid
       * @returns True if all metadata is valid
       */
      metadataValid(): boolean {
        return this.imageUri !== '' && this.serviceName !== '';
      },
      /**
       * Removes any duplicate environment variables, and represents
       * as an map of key-value pairs
       * @returns Environment variables as a unique key-value pair
       */
      uniqueEnv(): Record<string, string> {
        const uniqueEnvs: Record<string, string> = {};
        this.env.forEach(({ key, value }) => {
          uniqueEnvs[key] = value;
        });
        return uniqueEnvs;
      },
    },
    actions: {
      /**
       * Populates the store with data from the inference service
       * TODO: Instead of assuming current user ID is
       * the owner ID, we should get the owner ID from
       * the route params
       * @param modelId Model to load inference service from
       * @param userId Associated owner ID that created said inference service
       * @returns Promise that resolves when data is loaded
       */
      async loadFromInferenceService(
        modelId: string,
        userId: string
      ): Promise<void> {
        const authStore = useAuthStore();
        const modelStore = useModelStore();
        const inferenceServiceStore = useInferenceServiceStore();

        const data = await modelStore.getModelById(userId, modelId);
        const serviceName = data.inferenceServiceName;

        if (!serviceName) {
          return Promise.reject('No inference service found');
        }

        // Get the inference service
        const service = await inferenceServiceStore.getServiceByName(
          serviceName
        );

        // Load the data
        this.imageUri = service.imageUri;
        this.containerPort = service.containerPort ?? undefined;
        this.serviceName = serviceName;

        // Load the env vars
        Object.entries(service.env ?? {}).forEach((val) => {
          this.env.push({
            key: val[0],
            value: val[1],
          });
        });
      },
      /**
       * Start a preview service to test the inference service
       * @param modelId Model to launch preview service for
       * @returns Promise that resolves when the service is launched
       */
      async launchPreviewService(modelId: string): Promise<void> {
        const inferenceServiceStore = useInferenceServiceStore();
        try {
          const { serviceName, inferenceUrl, status } =
            await inferenceServiceStore.launchPreviewService(
              modelId,
              this.imageUri,
              this.numGpus,
              this.containerPort,
              this.uniqueEnv
            );
          this.previewServiceName = serviceName;
          this.previewServiceUrl = inferenceUrl;
          this.previewServiceStatus = status;
          return Promise.resolve();
        } catch (error) {
          return Promise.reject(error);
        }
      },
      /**
       * Updates the inference service
       * @param userId User ID of the model owner
       * @param modelId  Model ID to update
       * @returns Promise that resolves when the service is updated
       */
      async updateInferenceService(
        userId: string,
        modelId: string | undefined
      ): Promise<void> {
        const inferenceServiceStore = useInferenceServiceStore();
        // Remove any existing preview service
        if (this.previewServiceName) {
          try {
            await inferenceServiceStore.deleteService(this.previewServiceName);
          } catch (error) {
            console.error(error);
          }
        }
        if (this.serviceName) {
          const { serviceName } = await inferenceServiceStore.updateService(
            this.serviceName,
            this.imageUri,
            this.numGpus,
            this.containerPort,
            this.uniqueEnv
          );
          // Check status of updated service
          const status = await inferenceServiceStore.getServiceReady(
            serviceName
          );
          if (status.ready) {
            return Promise.resolve();
          } else {
            return Promise.reject('Failed to update inference service');
          }
        } else {
          // Create a new service if none exists
          if (!modelId) {
            return Promise.reject('No model id provided');
          }
          const modelStore = useModelStore();
          const { serviceName } = await inferenceServiceStore.createService(
            modelId,
            this.imageUri,
            this.numGpus,
            this.containerPort,
            this.uniqueEnv
          );
          // Update service with serviceName
          await modelStore.updateModel(
            {
              inferenceServiceName: serviceName,
            },
            userId,
            modelId
          );
        }
      },
    },
  }
);
