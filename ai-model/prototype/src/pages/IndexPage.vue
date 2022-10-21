<template>
  <q-page class="row items-center justify-evenly">
    <gradio-frame url="localhost"></gradio-frame>
  </q-page>
</template>

<script setup lang="ts">
import GradioFrame from 'components/GradioFrame.vue';
import { ref } from 'vue';
</script>
