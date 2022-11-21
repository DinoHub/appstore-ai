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
    <!-- <gradio-app src="https://stabilityai-stable-diffusion.hf.space/"></gradio-app> -->
    <q-card-section>
      <q-inner-loading
        :showing="loading"
        label="Loading Inference App..."
      ></q-inner-loading>
    </q-card-section>
    <q-card-section>
      <iframe
        @load="loading = false"
        v-show="!loading"
        :src="iframeUrl"
      ></iframe>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, Ref, ref, computed, ComputedRef } from 'vue';

interface Props {
  url: string;
  dark?: boolean;
}

const props = defineProps<Props>();
const loading: Ref<boolean> = ref(true);

const iframeUrl: ComputedRef<string | undefined> = computed(() => {
  return props.url
    ? `${props.url}?__theme=${props.dark ? 'dark' : 'light'}`
    : undefined;
});
</script>
