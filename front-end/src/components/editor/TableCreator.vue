<template>
  <q-card>
    <q-card-section>
      <div class="text-h5">Create Table</div>
    </q-card-section>
    <q-card-section>
      <q-input
        outlined
        v-model="noRows"
        type="number"
        label="Number of Rows"
        :rules="[(val) => val > 0 || 'Please enter a number greater than 0']"
        min="0"
      ></q-input>
      <q-input
        outlined
        v-model="noCols"
        type="number"
        label="Number of Columns"
        :rules="[(val) => val > 0 || 'Please enter a number greater than 0']"
        min="0"
      ></q-input>
    </q-card-section>
    <q-card-actions>
      <q-btn
        label="Create Table"
        color="primary"
        @click="createTable"
        v-close-popup
      ></q-btn>
      <q-btn label="Cancel" color="red" v-close-popup></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const noRows = ref(3);
const noCols = ref(3);

const emit = defineEmits(['createTable']);

function createTable() {
  if (noRows.value < 1 || noCols.value < 1) {
    console.error('Cannot create table!');
    return;
  } else {
    emit('createTable', noRows.value, noCols.value);
  }
}
</script>
