<style>
#dashboardModels .q-table__grid-content {
  justify-content: flex-start;
}

.card-height {
  height: 100%;
}
</style>

<template>
  <q-page padding>
    <!-- content -->
    <main>
      <div class="row display-medium q-pl-md">
        Welcome Back, {{ username ?? 'User' }}
      </div>
      <section>
        <model-card-data-table
          id="dashboardModels"
          :pagination="pagination"
          :filter="filter"
          card-container-class="q-pa-md col-xs-12 col-sm-5 col-md-3"
          card-class="bg-surface-variant card-height"
          class="q-px-sm"
        >
          <template #top-left
            ><span class="display-small">Your Models</span></template
          >
        </model-card-data-table>
      </section>
    </main>
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add" color="tertiary" to="/model/create"></q-btn>
    </q-page-sticky>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ModelCardDataTable from 'src/components/content/ModelCardDataTable.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { Pagination, SearchFilter } from 'src/components/models';

const authStore = useAuthStore();
const username = ref(authStore.user?.name);

// Get all user models
const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
  creator: authStore.user?.userId ?? undefined,
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
