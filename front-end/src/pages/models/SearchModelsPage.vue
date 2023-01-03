<template>
  <q-page padding>
    <!-- content -->
    <q-layout view="hHh lpr fff">
      <q-page-container>
        <model-card-data-table
          :filter="filter"
          :filter-drawer="filterDrawer"
          :pagination="pagination"
          show-filter
          card-container-class="col-12 q-pa-sm"
          card-class="bg-surface-variant"
          title="Models"
        >
          <template #top-left>
            <div class="display-medium">Models</div>
          </template>
        </model-card-data-table>
      </q-page-container>
    </q-layout>
    <q-page-sticky position="bottom-right" :offset="[18, 5]">
      <q-btn
        fab-mini
        :icon="filterDrawer ? 'filter_list_off' : 'filter_list'"
        color="tertiary"
        @click="filterDrawer = !filterDrawer"
      ></q-btn>
    </q-page-sticky>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardDataTable from 'src/components/content/ModelCardDataTable.vue';
import { Pagination, SearchFilter } from 'src/components/models';
import { ref } from 'vue';

const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
};

const filterDrawer = ref(true);

const pagination: Pagination = {
  sortBy: {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true,
  },
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 1,
};
</script>
