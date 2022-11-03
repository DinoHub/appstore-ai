<style>
.search-card {
  width: 100%;
}
</style>
<template>
  <q-page padding>
    <!-- content -->
    <model-card-data-table
      :filter="filter"
      show-filter
      card-class="search-card"
      title="Models"
    >
      <template #top-left>
        <div class="text-h3">Models</div>
      </template>
    </model-card-data-table>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardDataTable from 'src/components/ModelCardDataTable.vue';
import { reactive, ref, Ref } from 'vue';
import { useModelStore } from 'src/stores/model-store';

const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
};
</script>
