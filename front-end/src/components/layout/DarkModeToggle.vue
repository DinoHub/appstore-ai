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
import { onMounted } from 'vue';
import { useQuasar } from 'quasar';
const $q = useQuasar();
const toggleDarkMode = () => {
  $q.dark.toggle();
  localStorage.setItem('theme', $q.dark.isActive ? 'dark' : 'light');
  if (document.documentElement.getAttribute('data-theme') === 'dark') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
};

onMounted(() => {
  // Check localStorage for theme
  // TODO: Move to a Settings pinia store when we have more settings
  // TODO: make settings account specific and not browser specific
  // to keep track of user's preferences
  const theme = localStorage.getItem('theme');
  $q.dark.set(theme === 'dark');
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
  }
});
</script>
