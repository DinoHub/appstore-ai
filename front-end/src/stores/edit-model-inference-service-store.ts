import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { useModelStore } from './model-store';
import { useInferenceServiceStore } from './inference-service-store';

export const useEditInferenceServiceStore = defineStore(
  'editInferenceService',
  {
    state: () => ({
      step: 1 as number,
      imageUri: '' as string,
      containerPort: null as number | null,
    }),
    getters: {},
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

        // Get the inference service
        const service = await inferenceServiceStore.getServiceByName(
          serviceName
        );

        // Load the data
        this.imageUri = service.imageUri;
        this.containerPort = service.containerPort ?? null;
      },
    },
  }
);
