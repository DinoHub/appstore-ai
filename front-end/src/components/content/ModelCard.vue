<style scoped>
/* Prevents text from overflowing the card */
.clamp-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Control position of action buttons */
.action-row {
  position: absolute;
  bottom: 5px;
  right: 5px;
}
</style>
<template>
  <q-card
    v-ripple
    class="cursor-pointer q-hoverable q-pa-sm"
    :class="props.cardClass"
    @click.stop="$router.push(`/model/${props.creatorUserId}/${props.modelId}`)"
  >
    <span class="q-focus-helper"></span>
    <q-card-section class="q-pb-sm">
      <div class="headline-small clamp-text">{{ props.title }}</div>
      <div>
        <!-- Display all tags -->
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
    <q-card-section class="clamp-text q-mb-xl q-pt-none">
      {{ props.description ?? 'No description provided' }}
    </q-card-section>
    <q-card-actions align="right" class="action-row" v-if="isModelOwner">
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
      <!-- TODO: Consider Delete button? -->
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { computed, defineProps } from 'vue';
import MaterialChip from './MaterialChip.vue';

export interface ModelCardProps {
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

const props = defineProps<ModelCardProps>();

const isModelOwner = computed(() => {
  return props.creatorUserId == authStore.user?.userId;
});
</script>
