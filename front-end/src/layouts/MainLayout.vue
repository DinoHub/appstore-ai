<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
          v-if="loggedIn"
        />

        <!-- <q-toolbar-title>

        </q-toolbar-title> -->

        <q-drawer v-model="leftDrawerOpen" bordered> </q-drawer>
        <q-toolbar-title
          ><router-link to="/" class="text-h6">
            <q-img
              src="../assets/aas_logo.png"
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
            to="/models/create"
            icon="add"
            v-if="loggedIn"
          />
        </div>
        <div class="q-pl-sm">
          <quick-search-modal v-if="loggedIn"></quick-search-modal>
        </div>
        <div class="q-pl-sm">
          <!-- Notifications -->
          <q-btn flat round color="white" icon="chat" v-if="loggedIn" />
        </div>
        <!-- <div class="q-pl-sm">
          <q-btn flat round color="white" icon="account_box" v-if="loggedIn" />
        </div> -->
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
    </q-header>
    <q-drawer v-model="leftDrawerOpen" bordered>
      <q-list>
        <q-item-label header> Links </q-item-label>
      </q-list>
    </q-drawer>

    <q-page-container>
      <route-breadcrumbs class="q-pt-md q-pl-md"></route-breadcrumbs>
      <router-view />
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <q-toolbar-title class="text-center text-caption"
          >2022 - DSTA</q-toolbar-title
        >
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { ref, computed } from 'vue';

import QuickSearchModal from 'src/components/QuickSearchModal.vue';
import RouteBreadcrumbs from 'src/components/RouteBreadcrumbs.vue';

const authStore = useAuthStore();

const loggedIn = computed(() => {
  return authStore.user && authStore.user?.userId !== null;
});

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function onLogout() {
  authStore.logout();
}
</script>
