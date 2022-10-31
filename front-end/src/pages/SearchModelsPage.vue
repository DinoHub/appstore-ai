<style>
.search-card {
  width: 100%;
}
</style>
<template>
  <q-page padding>
    <!-- content -->
    <model-card-data-table card-class="search-card" title="Models">
      <template #top-left>
        <div class="text-h3">Models</div>
      </template>
    </model-card-data-table>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardDataTable from 'src/components/ModelCardDataTable.vue';
</script>
