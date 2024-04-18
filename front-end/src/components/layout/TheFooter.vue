<template>
  <q-toolbar class="bg-dark">
    <q-toolbar-title class="text-center text-caption"
      ><div>{{ currentYear }} - DSTA Digital Hub </div> <div> Frontend Version: {{ frontendVersion }} | Backend Version: {{ backendVersion }}</div></q-toolbar-title
    >
  </q-toolbar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
const currentYear = computed(() => new Date().getFullYear());
const frontendVersion = process.env.FRONTEND_VERSION;
const backendVersion = process.env.BACKEND_VERSION;
</script>
