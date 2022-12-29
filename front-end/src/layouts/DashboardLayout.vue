<template>
  <q-layout view="hHh lpR fff">
    <q-header elevated>
      <the-navbar
        @toggle-nav-rail="navSidebarOpen = !navSidebarOpen"
      ></the-navbar>
    </q-header>

    <q-drawer v-model="activitiesDrawerOpen" side="right">
      <!-- drawer content -->
    </q-drawer>
    <q-drawer :width="120" v-model="navSidebarOpen" show-if-above side="left">
      <nav-rail></nav-rail>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer>
      <the-footer></the-footer>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import TheNavbar from 'src/components/layout/TheNavbar.vue';
import TheFooter from 'src/components/layout/TheFooter.vue';
import NavRail from 'src/components/layout/NavRail.vue';

import { ref } from 'vue';
const activitiesDrawerOpen = ref(false);
const navSidebarOpen = ref(true);
</script>
