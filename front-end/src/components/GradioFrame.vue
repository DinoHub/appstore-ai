<style scoped>
.gradio-container iframe {
  width: 100%;
  height: 90vh;
}
</style>
<template>
  <div class="gradio-container">
    <gradio-app src="https://stabilityai-stable-diffusion.hf.space/"></gradio-app>
    <!-- <iframe :src="props.url"></iframe> -->
  </div>
</template>

<script setup lang="ts">
import { defineProps, onMounted } from 'vue';

interface Props {
  url: string;
}

const props = defineProps<Props>();

onMounted(() => {
  function make_script(src: string): void {
    const script = document.createElement('script');
    script.type = 'module';
    script.setAttribute('crossorigin', '');
    script.src = src;
    document.head.appendChild(script);
  }
  make_script(
    'https://gradio.s3-us-west-2.amazonaws.com/3.9/assets/index.d8955b2b.js'
  );
});
</script>
