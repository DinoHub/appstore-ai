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
            card-class="col-12"
          >
            <template #top-left>
              <div class="text-h4">Quick Search</div>
            </template>
          </model-card-data-table>
        </q-card-section>
      </q-card>
    </q-dialog>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ModelCardDataTable from './ModelCardDataTable.vue';
import { Pagination } from './models';

const search = ref(false);
const filter: SearchFilter = {};

const pagination: Pagination = {
  sortBy: '_id',
  descending: false,
  page: 1,
  rowsPerPage: 5,
  rowsNumber: 1,
};
</script>
