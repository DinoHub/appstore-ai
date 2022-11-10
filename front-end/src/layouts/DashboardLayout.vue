<template>
  <q-layout view="hHh lpR fff">
    <q-header elevated>
      <the-navbar></the-navbar>
    </q-header>

    <q-drawer v-model="rightDrawerOpen" side="right">
      <!-- drawer content -->
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
import TheNavbar from 'src/components/TheNavbar.vue';
import TheFooter from 'src/components/TheFooter.vue';
import { ref, Ref } from 'vue';
const rightDrawerOpen: Ref<boolean> = ref(false);
</script>
