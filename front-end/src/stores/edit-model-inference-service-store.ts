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
      metadataValid(): boolean {
        return this.imageUri !== '' && this.serviceName !== '';
      },
      uniqueEnv(): Record<string, string> {
        const uniqueEnvs: Record<string, string> = {};
        this.env.forEach(({ key, value }) => {
          uniqueEnvs[key] = value;
        });
        return uniqueEnvs;
      },
    },
    actions: {
      async loadFromInferenceService(modelId: string): Promise<void> {
        const authStore = useAuthStore();
        const modelStore = useModelStore();
        const inferenceServiceStore = useInferenceServiceStore();

        const data = await modelStore.getModelById(
          authStore.user?.userId ?? '',
          modelId
        );
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
      async launchPreviewService(modelId: string) {
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
      async updateInferenceService(userId: string, modelId: string | undefined) {
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
