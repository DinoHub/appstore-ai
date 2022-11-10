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
      <q-chip
        clickable
        color="primary"
        text-color="white"
        :label="props.task"
        @click.stop="$router.push(`/models/?tasks=${props.task}`)"
      >
      </q-chip>
      <q-chip
        v-for="tag in props.frameworks"
        :key="tag"
        clickable
        color="accent"
        text-color="white"
        :label="tag"
        @click.stop="$router.push(`/models/?frameworks=${tag}`)"
      >
      </q-chip>
      <q-chip
        v-for="tag in props.tags"
        :key="tag"
        clickable
        color="secondary"
        text-color="white"
        @click.stop="$router.push(`/models/?tags=${tag}`)"
        :label="tag"
      >
      </q-chip>
    </q-card-section>
    <q-card-section>
      {{ props.summary ?? 'No summary provided' }}
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions align="right" v-if="isModelOwner">
      <q-btn
        rounded
        color="primary"
        label="Edit"
        text-color="white"
        padding="xs xl"
        @click.stop
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
