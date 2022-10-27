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
        :to="`models/${creatorUserId}/${modelId}`"
      ></q-btn>
      <q-btn
        flat
        label="Edit"
        text-color="primary"
        :to="`models/${creatorUserId}/${modelId}/edit`"
        v-if="isModelOwner"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { computed, defineProps, withDefaults } from 'vue';

export interface ModelCardProps {
  creatorUserId: string;
  modelId: string;
  title: string;
  description: string;
  tags: string[];
}

const authStore = useAuthStore();
const props = withDefaults(defineProps<ModelCardProps>(), {
  creatorUserId: 'dev1',
  modelId: 'bert',
  title: 'Card Title',
  description: 'Sample description',
  tags: () => {
    return ['Example 1', 'Example 2'];
  },
});

const isModelOwner = computed(() => {
  return props.creatorUserId == authStore.user?.userId;
});
</script>
