<style scoped>
/* TODO: Figure out how to make the width consistent even if no text */
.log-view {
  max-width: 100ch;
  height: 75vh;
  overflow: auto;
}
</style>

<template>
  <q-card class="bg-black text-white">
    <q-card-section>
      <code class="log-view">
        {{ message }}
      </code>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
interface SSELogStreamProps {
  endpoint: string; // URL of the server-sent event stream
}

const props = defineProps<SSELogStreamProps>();
const fullURL = computed(() => {
  // Check if the endpoint is a full URL
  // If so, use it as-is
  if (props.endpoint.startsWith('http')) {
    return props.endpoint;
  }
  // Otherwise, assume it's a call to the backend
  return `${process.env.API}/${props.endpoint}`;
});

const message = ref('');
// It is assumed that the back-end returns a server-sent event stream
const eventSource = new EventSource(fullURL.value, { withCredentials: true });
eventSource.onmessage = (event) => {
  message.value = event.data;
};
</script>
