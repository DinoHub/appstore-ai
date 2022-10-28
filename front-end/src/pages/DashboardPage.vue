<template>
  <q-page padding>
    <!-- content -->
    <div class="text-h3">Welcome Back, {{ username ?? 'User' }}</div>
    <main>
      <section>
          <model-card-data-table
            :rows="currentUserModels"
          ></model-card-data-table>
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
const currentUserModels: Ref<ModelCardSummary[]> = ref([]);
if (authStore.user?.userId) {
  modelStore.getModelsByUser(authStore.user.userId).then((result) => {
    currentUserModels.value = result;
  });
}
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
