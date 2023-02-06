<template>
  <q-toolbar class="bg-dark">
    <!-- Button to open  navrail -->
    <!-- as navrail is in layout, we need to emit events to communicate with it -->
    <q-btn
      v-if="loggedIn"
      flat
      round
      dense
      icon="menu"
      aria-label="Menu"
      @click="$emit('toggle-nav-rail')"
    ></q-btn>
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
      <quick-search-modal v-if="loggedIn"></quick-search-modal>
    </div>
    <!-- <div class="q-pl-sm"> -->
    <!-- Notifications -->
    <!-- <notifications-menu v-if="loggedIn"></notifications-menu> -->
    <!-- </div> -->
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

import QuickSearchModal from 'src/components/layout/QuickSearchModal.vue';
// import NotificationsMenu from 'src/components/NotificationsMenu.vue';
import DarkModeToggle from './DarkModeToggle.vue';

const authStore = useAuthStore();
const emit = defineEmits(['toggle-nav-rail']);

const loggedIn = computed(() => authStore.user && authStore.user !== null);
const onLogout = () => authStore.logout();
</script>
