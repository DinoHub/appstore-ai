<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
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
              height="50px"
              fit="scale-down"
            ></q-img></router-link
        ></q-toolbar-title>

        <div class="q-pl-sm">
          <q-btn
            flat
            round
            color="white"
            to="/createModel"
            icon="add"
            v-if="loggedIn"
          />
        </div>
        <div class="q-pl-sm">
          <q-btn flat round color="white" icon="search" v-if="loggedIn" />
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
    <!-- TODO: Add dynamic breadcrumbs -->
    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <q-toolbar-title class="text-center text-caption">2022 - DSTA</q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { ref, computed } from 'vue';

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
