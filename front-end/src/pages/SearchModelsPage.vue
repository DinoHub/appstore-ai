<template>
  <q-page padding>
    <!-- content -->
    <model-card-data-table
      :filter="filter"
      :pagination="pagination"
      show-filter
      card-container-class="col-12 q-pa-sm"
      title="Models"
    >
      <template #top-left>
        <div class="text-h3">Models</div>
      </template>
    </model-card-data-table>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardDataTable from 'src/components/content/ModelCardDataTable.vue';
import { reactive, ref, Ref } from 'vue';
import { useModelStore } from 'src/stores/model-store';
import { Pagination } from 'src/components/models';

const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
};

const pagination: Pagination = {
  sortBy: {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true
  },
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 1,
};
</script>
