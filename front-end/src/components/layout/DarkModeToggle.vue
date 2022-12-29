<template>
  <q-btn
    flat
    dense
    round
    :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
    @click="toggleDarkMode"
  />
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
const $q = useQuasar();
const toggleDarkMode = () => {
  $q.dark.toggle();
  if (document.documentElement.getAttribute('data-theme') === 'dark') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
};
</script>
