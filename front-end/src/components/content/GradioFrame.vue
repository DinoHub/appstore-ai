<style scoped>
.gradio-container iframe {
  width: 100%;
  height: 50vh;
  border: none;
  border-radius: 0.5rem;
}
</style>
<template>
  <q-card class="gradio-container bg-white">
    <q-card-section>
      <!-- Display status of app -->
      <h6>
        {{
          serviceInstanceAvailable
            ? 'Manage Inference Service'
            : 'Service is Not Available'
        }}
      </h6>
      <p>
        {{ props.status?.message ?? 'No status message available' }}
      </p>
      <!-- Display number of replicas-->
      <!-- Offer option to scale, restore, or re-ping status -->
      <q-btn
        v-if="serviceInstanceAvailable"
        rounded
        no-caps
        padding="sm xl"
        label="Shut Down Instance"
        @click="scaleDown"
      ></q-btn>
      <q-btn
        v-else
        rounded
        no-caps
        padding="sm xl"
        label="Request New Instance"
        @click="scaleUp"
      ></q-btn>
    </q-card-section>
    <q-card-section>
      <q-inner-loading
        v-if="loading"
        :showing="loading"
        label="Loading Inference App..."
      >
        <q-spinner-gears size="100px" color="primary"></q-spinner-gears>
      </q-inner-loading>
      <iframe
        @load="loading = false"
        v-show="!loading"
        :src="iframeUrl"
      ></iframe>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, ref, computed, ComputedRef } from 'vue';
import {
  InferenceServiceStatus,
  useInferenceServiceStore,
} from 'src/stores/inference-service-store';
import { useRouter } from 'vue-router';

interface GradioFrameProps {
  url: string;
  dark?: boolean;
  status?: InferenceServiceStatus;
}

const props = defineProps<GradioFrameProps>();
// const status = ref(props.status);
const inferenceServiceStore = useInferenceServiceStore();
const loading = ref(true);
const router = useRouter();

const iframeUrl: ComputedRef<string | undefined> = computed(() => {
  return props.url
    ? `${props.url}?__theme=${props.dark ? 'dark' : 'light'}`
    : undefined;
});

const serviceInstanceAvailable = computed(() => {
  return (props.status?.expectedReplicas ?? 0) > 0;
});

const scaleUp = () => {
  if (props.status?.serviceName) {
    inferenceServiceStore
      .scaleService(props.status?.serviceName, 1)
      .then(() => {
        inferenceServiceStore
          .getServiceReady(props.status?.serviceName ?? '')
          .then(() => {
            router.go(0);
          })
          .catch((err) => {
            console.error(err);
          });
      })
      .catch((err) => {
        console.error(err);
      });
  }
};

const scaleDown = () => {
  if (props.status?.serviceName) {
    inferenceServiceStore
      .scaleService(props.status?.serviceName, 0)
      .then(() => {
        // router.go(0);
        window.location.reload();
      })
      .catch((err) => {
        console.error(err);
      })
      .then(() => {
        // router.go(0);
        window.location.reload();
      });
  }
};
</script>
