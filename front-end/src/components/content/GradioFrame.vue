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
      <div class="text-right">
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
              <q-item-section>Scale Down Instance </q-item-section>
            </q-item>
            <q-item v-else v-close-popup clickable @click="scaleUp"
              ><q-item-section>Request New Instance</q-item-section>
            </q-item>
            <q-item v-if="props.debugMode" clickable @click="showLogs = true">
              <q-item-section>View Logs</q-item-section>
            </q-item>
          </q-menu>
        </q-btn>
      </div>
    </q-card-section>
    <q-card-section v-if="props.status?.message !== ''">
      {{ props.status?.message }}
    </q-card-section>
    <q-card-section v-if="props.status?.expectedReplicas == 0">
      No instances available. Click the settings button to request a new
      instance.
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
        v-show="!loading"
        :src="iframeUrl"
      ></iframe>
    </q-card-section>
    <q-inner-loading :showing="processing">
      <q-spinner color="primary" size="50px" />
    </q-inner-loading>
    <q-dialog v-model="showLogs">
      <q-card>
        <q-card-section>
          <SSE-log-stream
            :endpoint="'engines/' + props.status?.serviceName + '/logs'"
          ></SSE-log-stream>
        </q-card-section>
        <q-card-actions>
          <div class="q-ml-sm">
            <q-btn
              rounded
              no-caps
              padding="sm xl"
              color="primary"
              label="Close"
              @click="showLogs = false"
            />
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, ref, computed, ComputedRef } from 'vue';
import SSELogStream from './SSELogStream.vue';
import {
  InferenceServiceStatus,
  useInferenceServiceStore,
} from 'src/stores/inference-service-store';
import { useRouter } from 'vue-router';

interface GradioFrameProps {
  url: string;
  dark?: boolean;
  debugMode?: boolean;
  status?: InferenceServiceStatus;
}

const props = defineProps<GradioFrameProps>();
// const status = ref(props.status);
const inferenceServiceStore = useInferenceServiceStore();
const loading = ref(true);
const processing = ref(false);
const showLogs = ref(false);
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
          })
          .finally(() => {
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
      });
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
