<template>
  <q-card>
    <q-card-section>
      <h6>{{ title }}</h6>
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
        :to="`models/${id}`"
      ></q-btn>
      <q-btn
        flat
        label="Edit"
        text-color="primary"
        :to="`models/${id}/edit`"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { defineProps, withDefaults } from 'vue';

export interface ModelCardProps {
  id: string;
  title: string;
  description: string;
  tags: string[];
}
const props = withDefaults(defineProps<ModelCardProps>(), {
  title: 'Card Title',
  description: 'Sample description',
  tags: () => {
    return ['Example 1', 'Example 2'];
  },
});
</script>
