<template>
  <q-layout view="hHh Lpr fff">
    <q-header elevated>
      <the-navbar
        @toggle-nav-rail="navSidebarOpen = !navSidebarOpen"
      ></the-navbar>
    </q-header>
    <q-page-container>
      <route-breadcrumbs class="q-pt-md q-pl-md"></route-breadcrumbs>
      <router-view />
    </q-page-container>
    <q-drawer :width="120" v-model="navSidebarOpen" show-if-above side="left">
      <nav-rail></nav-rail>
    </q-drawer>
    <q-footer>
      <the-footer></the-footer>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import TheFooter from 'src/components/layout/TheFooter.vue';
import TheNavbar from 'src/components/layout/TheNavbar.vue';
import RouteBreadcrumbs from 'src/components/layout/RouteBreadcrumbs.vue';
import NavRail from 'src/components/layout/NavRail.vue';

import { ref } from 'vue';
const navSidebarOpen = ref(true);
</script>
