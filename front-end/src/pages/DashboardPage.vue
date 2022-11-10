<style>
#dashboardModels .q-table__grid-content {
  justify-content: flex-start;
}
</style>

<template>
  <q-page padding>
    <!-- content -->
    <main>
      <div class="row text-h4 q-px-xl">Welcome Back, {{ username ?? 'User' }}</div>
      <div class="row q-px-xl q-py-sm">
        <div class="col-auto text-h5 self-center">
          Your Models
        </div>
        <div class="col-auto q-px-md">
          <q-btn round icon="add" to="/models/create"></q-btn>
        </div>
        <div class="col-auto q-pl-sm self-center">
          <q-btn flat label="View all models" to="/models"></q-btn>
        </div>
      </div>
      <section>
        <model-card-data-table
          id="dashboardModels"
          :pagination="pagination"
          :filter="filter"
          card-container-class="q-pa-md col-xs-12 col-sm-5 col-md-3"
          class="q-px-sm"
        >
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
import { Pagination, SearchFilter } from '../components/models';

const authStore = useAuthStore();
const username = ref(authStore.user?.name);

// Get all user models
const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
  creator: authStore.user?.userId,
};

const pagination: Pagination = {
  sortBy: {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true,
  },
  descending: false,
  page: 1,
  rowsPerPage: 6,
  rowsNumber: 1,
};
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
