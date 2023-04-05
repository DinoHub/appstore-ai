<template>
  <div>
    <q-tabs shrink stretch>
      <q-route-tab
        :to="`/admin/models/${userId}/${modelId}/edit/metadata`"
        name="metadata"
        label="Edit Metadata"
        no-caps
      />
      <q-route-tab
        v-if="task != 'Reinforcement Learning'"
        :to="`/admin/models/${userId}/${modelId}/edit/inference`"
        name="service"
        label="Edit Inference Service"
        no-caps
      />
      <q-route-tab
        v-if="task == 'Reinforcement Learning'"
        :to="`/admin/models/${userId}/${modelId}/edit/video`"
        name="video"
        label="Edit Example Video"
        no-caps
      />
    </q-tabs>
  </div>
</template>

<script lang="ts">
export default {
  props: ['task'],
};
</script>

<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();

const modelId = route.params.modelId as string;
const userId = route.params.userId as string;
</script>
