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
        />

        <q-toolbar-title> AI App Store </q-toolbar-title>

        <div class="q-pl-sm">
          <q-btn flat round color="white" to="/createModel" icon="add" />
        </div>
        <div class="q-pl-sm">
          <q-btn flat round color="white" icon="search" />
        </div>
        <div class="q-pl-sm">
          <q-btn flat round color="white" icon="chat" />
        </div>
        <div class="q-pl-sm">
          <q-btn flat round color="white"  icon="account_box" />
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" bordered>
      <q-list>
        <q-item-label header> Essential Links </q-item-label>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
