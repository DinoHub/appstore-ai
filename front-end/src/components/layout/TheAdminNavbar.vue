<template>
  <q-toolbar class="bg-dark">
    <q-toolbar-title
      ><router-link to="/admin" class="text-h6">
        <q-img
          src="../../assets/aas_logo.png"
          height="0"
          fit="scale-down"
          position="2% 50%"
          class="q-py-lg"
        ></q-img></router-link
    ></q-toolbar-title>
    <q-tabs shrink inline-label>
      <q-route-tab
        exact
        icon="supervised_user_circle"
        label="Users"
        to="/admin"
      />
      <q-route-tab exact icon="devices" label="Models" to="/admin/models" />
      <q-route-tab
        exact
        icon="import_export"
        label="Exports"
        to="/admin/exports"
      />
    </q-tabs>
    <div class="q-pl-sm">
      <dark-mode-toggle></dark-mode-toggle>
    </div>
    <div class="q-pl-sm">
      <q-btn
        flat
        dense
        round
        icon="logout"
        aria-label="Logout"
        @click="onLogout"
        v-if="loggedIn"
      ></q-btn>
    </div>
  </q-toolbar>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { computed, ref } from 'vue';

import DarkModeToggle from './DarkModeToggle.vue';

const authStore = useAuthStore();

const loggedIn = computed(() => authStore.user && authStore.user !== null);
const onLogout = () => authStore.admin_logout();
</script>
