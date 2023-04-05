<template>
  <q-toolbar class="bg-dark">
    <q-toolbar-title class="text-center text-caption"
      >{{ currentYear }} - DSTA Digital Hub</q-toolbar-title
    >
  </q-toolbar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
const currentYear = computed(() => new Date().getFullYear());
</script>
