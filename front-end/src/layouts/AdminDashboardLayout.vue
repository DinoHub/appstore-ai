<template>
  <q-layout view="hHh Lpr fff">
    <q-header elevated>
      <the-navbar></the-navbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
    <q-footer elevated>
      <the-footer></the-footer>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import TheNavbar from 'src/components/layout/TheAdminNavbar.vue';
import TheFooter from 'src/components/layout/TheFooter.vue';

import { ref, Ref } from 'vue';
const activitiesDrawerOpen: Ref<boolean> = ref(false);
const navSidebarOpen: Ref<boolean> = ref(true);
</script>
