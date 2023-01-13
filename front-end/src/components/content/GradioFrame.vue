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
      <!-- Display status of app if anything wrong -->
      <q-badge
        rounded
        :color="statusColor"
        :label="'Service Status: ' + props.status?.status"
      ></q-badge>
      <q-btn flat round color="secondary" icon="settings">
        <q-menu>
          <q-item
            v-if="serviceInstanceAvailable"
            clickable
            v-close-popup
            @click="scaleDown"
          >
            <q-item-section> Scale Down Instance </q-item-section>
          </q-item>
          <q-item v-else v-close-popup clickable @click="scaleUp"
            ><q-item-section>Request New Instance</q-item-section>
          </q-item>
        </q-menu>
      </q-btn>
    </q-card-section>
    <q-card-section v-if="props.status?.message !== ''">
      {{ props.status?.message }}
    </q-card-section>
    <q-card-section v-if="props.status?.expectedReplicas == 0">
      No instances available. Click the settings button to request a new instance.
    </q-card-section>
    <q-card-section v-show="!(props.status?.expectedReplicas == 0)">
      <q-skeleton
        v-if="loading"
        :dark="dark"
        square
        width="100%"
        height="500px"
        animation="fade"
      >
      </q-skeleton>
      <iframe
        @load="loading = false"
        v-show="!loading "
        :src="iframeUrl"
      ></iframe>
    </q-card-section>
    <q-inner-loading :showing="processing">
      <q-spinner color="primary" size="100%" />
    </q-inner-loading>
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
const processing = ref(false);
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
    processing.value = true;
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
          }).finally(() => {
            processing.value = false;
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
  }
};

const statusColor = computed(() => {
  switch (props.status?.status) {
    case 'Running':
      return 'positive';
    case 'Pending':
      return 'warning';
    case 'Failed':
      return 'negative';
    default:
      return 'secondary';
  }
});
</script>
