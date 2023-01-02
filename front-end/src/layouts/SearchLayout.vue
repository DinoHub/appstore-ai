<template>
  <q-layout view="hHh Lpr fff">
    <q-header elevated>
      <the-navbar
        @toggle-nav-rail="navSidebarOpen = !navSidebarOpen"
      ></the-navbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
    <q-drawer :width="120" v-model="navSidebarOpen" show-if-above side="left">
      <nav-rail></nav-rail>
    </q-drawer>
    <q-footer elevated>
      <the-footer></the-footer>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import TheFooter from 'src/components/layout/TheFooter.vue';
import TheNavbar from 'src/components/layout/TheNavbar.vue';
import NavRail from 'src/components/layout/NavRail.vue';

import { ref } from 'vue';
const navSidebarOpen = ref(true);
</script>
