<style scoped>
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
  endpoint: string;
}

const props = defineProps<SSELogStreamProps>();
const fullURL = computed(() => {
  // Check if the endpoint is a full URL
  if (props.endpoint.startsWith('http')) {
    return props.endpoint;
  }
  // Otherwise, assume it's a call to the backend
  return `${process.env.API}/${props.endpoint}`;
});

const message = ref('');
const eventSource = new EventSource(fullURL.value, { withCredentials: true });
eventSource.onmessage = (event) => {
  message.value = event.data;
};
</script>
