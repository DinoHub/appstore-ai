<style scoped>
.q-card {
  max-width: fit-content;
  width: 80vw;
}
</style>
<template>
  <section>
    <q-btn
      flat
      round
      color="white"
      icon="search"
      @click="search = true"
    ></q-btn>
    <q-dialog v-model="search">
      <q-card class="q-px-xl q-py-md">
        <q-card-section>
          <model-card-data-table
            :pagination="pagination"
            :filter="filter"
            card-container-class="col-12 q-pa-sm"
            card-class="bg-surface-variant"
          >
            <template #top-left>
              <div class="display-medium">Quick Search</div>
            </template>
          </model-card-data-table>
        </q-card-section>
      </q-card>
    </q-dialog>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ModelCardDataTable from 'src/components/content/ModelCardDataTable.vue';
import { Pagination, SearchFilter } from '../models';

const search = ref(false);
const filter: SearchFilter = {};

const pagination: Pagination = {
  sortBy: {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true,
  },
  descending: false,
  page: 1,
  rowsPerPage: 4,
  rowsNumber: 1,
};
</script>
