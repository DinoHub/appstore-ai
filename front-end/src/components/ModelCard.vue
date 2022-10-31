<template>
  <q-card :class="props.cardClass">
    <q-card-section>
      <div class="text-h6">{{ props.title }}</div>
      <q-chip
        v-for="tag in props.tags"
        :key="tag"
        color="primary"
        text-color="white"
      >
        {{ tag }}
      </q-chip>
      <q-chip
        v-for="tag in props.frameworks"
        :key="tag"
        color="primary"
        text-color="white"
      >
        {{ tag }}
      </q-chip>
    </q-card-section>
    <q-card-section>
      {{ props.summary ?? 'No summary provided' }}
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions>
      <q-btn
        flat
        label="View"
        text-color="primary"
        :to="`models/${props.creatorUserId}/${props.modelId}`"
      ></q-btn>
      <q-btn
        flat
        label="Edit"
        text-color="primary"
        :to="`models/${props.creatorUserId}/${props.modelId}/edit`"
        v-if="isModelOwner"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { computed, defineProps } from 'vue';
export interface Props {
  creatorUserId: string;
  modelId: string;
  title: string;
  summary?: string;
  tags: string[];
  frameworks: string[];
  cardClass: string;
}
const authStore = useAuthStore();
const props = defineProps<Props>();

const isModelOwner = computed(() => {
  return props.creatorUserId == authStore.user?.userId;
});
</script>
