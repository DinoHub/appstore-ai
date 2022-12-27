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
      <iframe
        @load="loading = false"
        v-show="!loading"
        :src="iframeUrl"
      ></iframe>
    </q-card-section>
    <!-- <q-inner-loading :showing="loading" label="Loading Inference App...">
      <q-spinner-gears size="50px" color="primary"></q-spinner-gears>
    </q-inner-loading> -->
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, Ref, ref, computed, ComputedRef } from 'vue';

interface GradioFrameProps {
  url: string;
  dark?: boolean;
}

const props = defineProps<GradioFrameProps>();

const loading = ref(true);

const iframeUrl: ComputedRef<string | undefined> = computed(() => {
  return props.url
    ? `${props.url}?__theme=${props.dark ? 'dark' : 'light'}`
    : undefined;
});
</script>
