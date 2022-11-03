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
          <model-card-data-table :filter="filter" card-class="search-card">
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

const search = ref(false);
const filter: SearchFilter = {};
</script>
