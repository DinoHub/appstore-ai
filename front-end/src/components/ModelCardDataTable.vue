<template>
  <q-table
    grid
    title="Your models"
    :rows="rows"
    :columns="columns"
    :row-key="compositeId"
  >
    <template v-slot:item="props">
      <model-card
        class="q-ma-md"
        :title="props.row.title"
        :description="props.row.description"
        :model-id="props.row.modelId"
        :user-id="props.row.userId"
        :tags="props.row.tags"
      ></model-card>
    </template>
  </q-table>
</template>

<script setup lang="ts">
import ModelCard, { ModelCardProps } from './ModelCard.vue';
const columns = [
  {
    name: 'title',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'title',
  },
  {
    name: 'userId',
    required: true,
    label: 'Creator',
    field: 'userId',
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

const rows = [
  {
    title: 'BERT Large',
    userId: 'dev1',
    modelId: 'bert',
    description: 'Sample description',
    tags: ['Example Tag'],
  },
  {
    title: 'Superman',
    userId: 'dev1',
    modelId: 'bert',
    description: 'Sample description',
    tags: ['Example Tag'],
  },
];

function compositeId(row: ModelCardProps): string {
  return `${row.userId}/${row.modelId}`;
}
</script>
