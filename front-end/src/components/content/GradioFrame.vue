<style scoped>
.gradio-container iframe {
  width: 100%;
  height: 100vh;
  border: none;
  border-radius: 0.5rem;
}
</style>
<template>
  <q-card class="gradio-container bg-white">
    <!-- <gradio-app src="https://stabilityai-stable-diffusion.hf.space/"></gradio-app> -->
    <q-card-section>
      <iframe
        @load="loading = false"
        v-show="!loading"
        :src="props.url"
      ></iframe>
      <q-inner-loading
        :showing="loading"
        v-if="loading"
        label="Loading Inference App..."
      ></q-inner-loading>
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

// onMounted(() => {
//   function make_script(src: string): void {
//     const script = document.createElement('script');
//     script.type = 'module';
//     script.setAttribute('crossorigin', '');
//     script.src = src;
//     document.head.appendChild(script);
//   }
//   make_script(
//     'https://gradio.s3-us-west-2.amazonaws.com/3.9/assets/index.d8955b2b.js'
//   );
// });
</script>
