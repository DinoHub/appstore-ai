<template>
  <div>
    <q-tabs shrink stretch>
      <q-route-tab
        :to="`/model/${userId}/${modelId}/edit/metadata`"
        name="metadata"
        label="Edit Metadata"
        no-caps
      />
      <q-route-tab
        :to="`/model/${userId}/${modelId}/edit/inference`"
        name="service"
        label="Edit Inference Service"
        no-caps
      />
    </q-tabs>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute();

const modelId = route.params.modelId as string;
const userId = route.params.userId as string;
</script>
