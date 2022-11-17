<template>
  <q-card
    v-ripple
    class="cursor-pointer q-hoverable q-pa-sm"
    :class="props.cardClass"
    @click.stop="$router.push(`/model/${props.creatorUserId}/${props.modelId}`)"
  >
    <span class="q-focus-helper"></span>
    <q-card-section>
      <div class="headline-small">{{ props.title }}</div>
      <div>
        <material-chip
          :label="props.task"
          type="task"
          clickable
          @click.stop="$router.push(`/models?tasks=${props.task}`)"
        />
        <material-chip
          v-for="tag in props.frameworks"
          :key="tag"
          :label="tag"
          type="framework"
          clickable
          @click.stop="$router.push(`/models?frameworks=${tag}`)"
        >
        </material-chip>
        <material-chip
          v-for="tag in props.tags"
          :key="tag"
          :label="tag"
          type="tag"
          clickable
          @click.stop="$router.push(`/models?tags=${tag}`)"
        >
        </material-chip>
      </div>
    </q-card-section>
    <q-card-section>
      {{ props.description ?? 'No description provided' }}
    </q-card-section>
    <q-card-actions align="right" v-if="isModelOwner">
      <q-btn
        outline
        rounded
        no-caps
        color="outline"
        text-color="on-outline"
        label="Edit Model Card"
        padding="sm md"
        :to="`model/${props.creatorUserId}/${props.modelId}/edit/metadata`"
        @click.stop
        v-if="isModelOwner"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { computed, defineProps } from 'vue';
import MaterialChip from './MaterialChip.vue';

export interface Props {
  creatorUserId: string;
  modelId: string;
  title: string;
  description?: string;
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
