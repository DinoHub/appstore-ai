<template>
  <!-- TODO: Improve the table creator (e.g add rows, columns) -->
  <q-card>
    <q-card-section>
      <div class="text-h5">Create Table</div>
    </q-card-section>
    <q-card-section>
      <q-input
        rounded
        outlined
        v-model="noRows"
        type="number"
        label="Number of Rows"
        :rules="[(val) => val > 0 || 'Please enter a number greater than 0']"
        min="0"
      ></q-input>
      <q-input
        rounded
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
        no-caps
        rounded
        padding="sm xl"
        label="Create Table"
        color="primary"
        @click="createTable"
        v-close-popup
      ></q-btn>
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        label="Cancel"
        color="red"
        v-close-popup
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { Notify } from 'quasar';
import { ref } from 'vue';
import { Editor } from '@tiptap/vue-3';

export interface TableCreatorProps {
  editor: Editor;
  defaultHeaderRow: boolean;
  defaultRows: number;
  defaultCols: number;
}

const props = withDefaults(defineProps<TableCreatorProps>(), {
  defaultHeaderRow: true,
  defaultRows: 3,
  defaultCols: 3,
});

const noRows = ref(props.defaultRows);
const noCols = ref(props.defaultCols);

const createTable = () => {
  if (noRows.value < 1 || noCols.value < 1) {
    Notify.create({
      message: 'Unable to create table',
      color: 'negative',
    });
    return;
  } else {
    props.editor
      ?.chain()
      .focus()
      .insertTable({
        rows: noRows.value,
        cols: noCols.value,
        withHeaderRow: props.defaultHeaderRow,
      })
      .run();
  }
};
</script>
