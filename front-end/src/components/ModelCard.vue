<style scoped>
.card {
  width: 25%;
}
</style>
<template>
  <q-card class="card q-gutter-sm">
    <q-card-section>
      <div class="text-h6">{{ title }}</div>
      <q-chip v-for="tag in tags" :key="tag" color="primary" text-color="white">
        {{ tag }}
      </q-chip>
    </q-card-section>
    <q-card-section>
      {{ description }}
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions>
      <q-btn
        flat
        label="View"
        text-color="primary"
        :to="`models/${userId}/${modelId}`"
      ></q-btn>
      <q-btn
        flat
        label="Edit"
        text-color="primary"
        :to="`models/${userId}/${modelId}/edit`"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, withDefaults } from 'vue';

export interface ModelCardProps {
  userId: string;
  modelId: string;
  title: string;
  description: string;
  tags: string[];
}
const props = withDefaults(defineProps<ModelCardProps>(), {
  userId: 'dev1',
  modelId: 'bert',
  title: 'Card Title',
  description: 'Sample description',
  tags: () => {
    return ['Example 1', 'Example 2'];
  },
});
</script>
