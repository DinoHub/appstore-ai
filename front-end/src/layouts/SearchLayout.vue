<template>
  <q-layout view="hHh Lpr fff">
    <q-header elevated>
      <the-navbar></the-navbar>
    </q-header>
    <q-page-container>
      <route-breadcrumbs class="q-pt-md q-pl-md"></route-breadcrumbs>
      <router-view />
    </q-page-container>
    <q-footer elevated>
      <the-footer></the-footer>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import TheFooter from 'src/components/TheFooter.vue';
import TheNavbar from 'src/components/TheNavbar.vue';
import RouteBreadcrumbs from 'src/components/RouteBreadcrumbs.vue';
</script>
