<style>
.dashboard-card {
  width: 30%;
}
</style>
<template>
  <q-page padding>
    <!-- content -->
    <div class="text-h3">Welcome Back, {{ username ?? 'User' }}</div>
    <main>
      <section>
        <div class="row"></div>
        <model-card-data-table card-class="dashboard-card">
          <template v-slot:top-left>
            <div class="col col-sm-3 text-h4">
              Your Models
              <q-btn round icon="add" to="/models/create"></q-btn>
            </div>
            <router-link to="/models">View all models</router-link>
          </template>
        </model-card-data-table>
      </section>
    </main>
  </q-page>
</template>

<script setup lang="ts">
import { ref, Ref } from 'vue';
import ModelCardDataTable from 'src/components/ModelCardDataTable.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';

const authStore = useAuthStore();
const username = ref(authStore.user?.name);

// Get all user models
const modelStore = useModelStore();
// Get models owned by the user
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
