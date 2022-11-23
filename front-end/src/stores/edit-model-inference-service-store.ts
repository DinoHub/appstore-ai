import { Dialog } from 'quasar';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { useInferenceServiceStore } from './inference-service-store';
import { useModelStore } from './model-store';

export interface EnvField {
  key: string;
  value: string;
}

export const useEditInferenceServiceStore = defineStore(
  'editInferenceService',
  {
    state: () => ({
      step: 1 as number,
      imageUri: '' as string,
      containerPort: undefined as number | undefined,
      env: [] as EnvField[],
      serviceName: '' as string,
      previewServiceName: null as string | null,
      previewServiceUrl: null as string | null,
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
          modelId,
        );
        const serviceName = data.inferenceServiceName;

        // Get the inference service
        const service = await inferenceServiceStore.getServiceByName(
          serviceName,
        );

        // Load the data
        this.imageUri = service.imageUri;
        this.containerPort = service.containerPort ?? undefined;
        this.serviceName = serviceName;

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
          const { serviceName, inferenceUrl } =
            await inferenceServiceStore.launchPreviewService(
              modelId,
              this.imageUri,
              this.containerPort,
              this.uniqueEnv,
            );
          this.previewServiceName = serviceName;
          this.previewServiceUrl = inferenceUrl;
        } catch (error) {
          return Promise.reject(error);
        }
      },
      async updateInferenceService() {
        const inferenceServiceStore = useInferenceServiceStore();
        const { serviceName } = await inferenceServiceStore.updateService(
          this.serviceName,
          this.imageUri,
          this.containerPort,
          this.uniqueEnv,
        );
        // Check status of updated service
        const ready = await inferenceServiceStore.getServiceReady(serviceName);
        if (ready) {
          return Promise.resolve();
        } else {
          return Promise.reject('Failed to update inference service');
        }
      },
    },
  },
);
