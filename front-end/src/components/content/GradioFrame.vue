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
        <q-btn
          flat
          round
          color="secondary"
          icon="settings"
          id="gradio-settings-menu"
        >
          <q-menu>
            <!-- If replicas > 0, then show button to scale replicas to 0 -->
            <q-item
              v-if="serviceInstanceAvailable"
              clickable
              v-close-popup
              @click="scaleDown"
            >
              <q-item-section>Scale Down Instance </q-item-section>
            </q-item>
            <!-- Else, show button scale replicas to 1 -->
            <q-item v-else v-close-popup clickable @click="scaleUp"
              ><q-item-section>Request New Instance</q-item-section>
            </q-item>
            <!-- Logs are hidden to all but owner and admin -->
            <q-item v-if="props.debugMode" clickable @click="showLogs = true">
              <q-item-section>View Logs</q-item-section>
            </q-item>
            <q-item clickable @click="showDetailedStatus = true">
              <q-item-section>View Status</q-item-section>
            </q-item>
          </q-menu>
        </q-btn>
      </div>
    </q-card-section>
    <q-card-section v-if="props.status?.message !== ''">
      <p>
        {{ props.status?.message }}
      </p>
    </q-card-section>
    <q-card-section v-if="!serviceInstanceAvailable">
      No instances available. Click the settings button to request a new
      instance.
    </q-card-section>
    <q-card-section v-show="serviceInstanceAvailable">
      <!-- Show loading effect -->
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
    <!-- The inner loading shows when attempting to scale up instance -->
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
    <q-dialog v-model="showDetailedStatus" persistent>
      <q-card>
        <q-card-section>
          <service-status-display
            :status="inferenceServiceStore.currentServiceStatus"
          />
        </q-card-section>
        <q-card-actions>
          <q-btn
            rounded
            no-caps
            padding="sm xl"
            v-close-popup
            label="Close"
          ></q-btn>
        </q-card-actions> </q-card
    ></q-dialog>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, ref, computed, ComputedRef } from 'vue';
import SSELogStream from './SSELogStream.vue';
import ServiceStatusDisplay from './ServiceStatusDisplay.vue';
import {
  InferenceServiceStatus,
  useInferenceServiceStore,
} from 'src/stores/inference-service-store';
import { useRouter } from 'vue-router';

interface GradioFrameProps {
  url: string; // URL of the gradio app
  dark?: boolean; // Whether to use dark theme
  debugMode?: boolean; // Show logs
  status?: InferenceServiceStatus; // Status of the inference service
}

const props = defineProps<GradioFrameProps>();

const router = useRouter();
const inferenceServiceStore = useInferenceServiceStore();

const loading = ref(true);
const processing = ref(false);
const showLogs = ref(false);
const showDetailedStatus = ref(false);

// When a gradio app is used, the param __theme is used to set the theme
// of the app. This is done by appending the param to the URL.
// Note that if the app is not a Gradio app, this will have no effect.
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
            // Refresh the page
            // to force the iframe to reload
            router.go(0);
          })
          .catch((err) => {
            console.error(err);
          })
          .finally(() => {
            // No matter what, stop the loading effect
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
        // for some reason
        // router.go(0) does not work
        // here, so browser reload is used
        window.location.reload();
      })
      .catch((err) => {
        console.error(err);
      });
  }
};

// Map the status to a color
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
