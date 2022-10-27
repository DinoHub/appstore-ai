<template>
  <q-table
    grid
    title="Your models"
    :rows="props.rows"
    :columns="columns"
    :row-key="compositeId"
  >
    <template v-slot:item="props">
      <model-card
        class="q-ma-md"
        :title="props.row.title"
        :description="props.row.description"
        :model-id="props.row.modelId"
        :creator-user-id="props.row.creatorUserId"
        :tags="props.row.tags"
      ></model-card>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import { ModelCardSummary } from 'src/stores/model-store';
import ModelCard from './ModelCard.vue';

export interface Props {
  rows: ModelCardSummary[];
}

const props = defineProps<Props>();

const columns = [
  {
    name: 'title',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'title',
  },
  {
    name: 'creatorUserId',
    required: true,
    label: 'Creator',
    field: 'creatorUserId',
  },
  {
    name: 'modelId',
    required: true,
  },
  {
    name: 'description',
    required: true,
    label: 'Description',
    field: 'description',
  },
  {
    name: 'tags',
    required: true,
    label: 'Tags',
    field: 'tags',
  },
];

function compositeId(row: ModelCardSummary): string {
  return `${row.creatorUserId}/${row.modelId}`;
}
</script>
