<template>
  <q-toolbar class="bg-dark">
    <q-toolbar-title
      ><router-link to="/" class="text-h6">
        <q-img
          src="../../assets/aas_logo.png"
          height="0"
          fit="scale-down"
          position="2% 50%"
          class="q-py-lg"
        ></q-img></router-link
    ></q-toolbar-title>

    <div class="q-pl-sm">
      <q-btn
        flat
        round
        color="white"
        to="/model/create"
        icon="add"
        v-if="loggedIn"
      />
    </div>
    <div class="q-pl-sm">
      <quick-search-modal v-if="loggedIn"></quick-search-modal>
    </div>
    <div class="q-pl-sm">
      <!-- Notifications -->
      <notifications-menu v-if="loggedIn"></notifications-menu>
    </div>
    <!-- <div class="q-pl-sm">
          <q-btn flat round color="white" icon="account_box" v-if="loggedIn" />
        </div> -->
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
import { computed } from 'vue';

import QuickSearchModal from 'src/components/QuickSearchModal.vue';
import NotificationsMenu from 'src/components/NotificationsMenu.vue';
import RouteBreadcrumbs from 'src/components/layout/RouteBreadcrumbs.vue';
import DarkModeToggle from './DarkModeToggle.vue';

const authStore = useAuthStore();

const loggedIn = computed(() => {
  return authStore.user && authStore.user?.userId !== null;
});

function onLogout() {
  authStore.logout();
}
</script>
