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
        :src="props.url + '?__theme=light'"
      ></iframe>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, Ref, ref } from 'vue';

interface Props {
  url: string;
}

const props = defineProps<Props>();
const loading: Ref<boolean> = ref(true);
</script>
