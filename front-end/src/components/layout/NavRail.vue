<style>
.tab-item {
  border-radius: 0.5rem;
}
</style>
<template>
  <nav>
    <q-tabs content-class="tab-item" active-color="on-secondary" active-bg-color="secondary" vertical>
      <q-route-tab no-caps icon="add" label="Submit Model" to="/model/create"></q-route-tab>
      <q-route-tab no-caps icon="dashboard" label="Dashboard" to="/"></q-route-tab>
      <q-route-tab no-caps icon="store" label="Models" to="/models"></q-route-tab>
      <!-- TODO: Make this dynamically link based on environment variable -->
      <!-- so we can point to an internally hosted documentation -->
      <q-route-tab no-caps icon="help" label="Help" href="https://dinohub.github.io/appstore-ai/user-guide/introduction.html" target="_blank"></q-route-tab>
    </q-tabs>
  </nav>
</template>

<script setup lang="ts"></script>
