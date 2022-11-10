<template>
  <q-card
    v-ripple
    class="cursor-pointer q-hoverable"
    :class="props.cardClass"
    @click="$router.push(`/model/${props.creatorUserId}/${props.modelId}`)"
  >
    <span class="q-focus-helper"></span>
    <q-card-section>
      <div class="text-h6">{{ props.title }}</div>
      <q-chip color="primary" text-color="white">
        <router-link class="router-link" :to="`/models/?tasks=${props.task}`">
          {{ props.task }}</router-link
        >
      </q-chip>
      <q-chip
        v-for="tag in props.frameworks"
        :key="tag"
        color="accent"
        text-color="white"
      >
        <router-link class="router-link" :to="`/models/?frameworks=${tag}`">{{
          tag
        }}</router-link>
      </q-chip>
      <q-chip
        v-for="tag in props.tags"
        :key="tag"
        color="secondary"
        text-color="white"
      >
        <router-link class="router-link" :to="`/models/?tags=${tag}`">{{
          tag
        }}</router-link>
      </q-chip>
    </q-card-section>
    <q-card-section>
      {{ props.summary ?? 'No summary provided' }}
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions v-if="isModelOwner">
      <!-- <q-btn
        flat
        label="View"
        text-color="primary"
        :to="`/models/${props.creatorUserId}/${props.modelId}`"
      ></q-btn> -->
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
  task: string;
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
