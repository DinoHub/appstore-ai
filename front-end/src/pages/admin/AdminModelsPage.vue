<template>
  <div>
    <q-page padding>
      <!-- content -->
      <main>
        <div class="row justify-center">
          <div class="col-11 display-medium q-pl-md q-mt-xl">Models</div>
        </div>
        <section>
          <admin-model-data-table
            :pagination="pagination"
            :filter-drawer="filterDrawer"
            :show-filter="filterDrawer"
            :filter="filter"
          ></admin-model-data-table>
        </section>
      </main>
    </q-page>
    <q-page-sticky position="top-left" :offset="[7, 10]">
      <q-btn
        fab-mini
        :icon="filterDrawer ? 'keyboard_arrow_left' : 'keyboard_arrow_right'"
        color="tertiary"
        @click="filterDrawer = !filterDrawer"
      ></q-btn>
    </q-page-sticky>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Pagination, SearchFilter } from 'src/components/components/models';
import AdminModelDataTable from 'src/components/content/AdminModelDataTable.vue';

const filterDrawer = ref(true);
const pagination: Pagination = {
  sortBy: '_id',
  descending: true,
  page: 1,
  rowsNumber: 1,
};
const filter: SearchFilter = {
  title: '',
  creator: '',
  tasks: [],
  tags: [],
  frameworks: [],
};
</script>
