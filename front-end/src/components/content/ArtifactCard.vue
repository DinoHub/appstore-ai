<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">{{ props.name }}</div>
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions>
      <q-btn
        flat
        :href="props.url"
        label="View/Download"
        color="primary"
        target="_blank"
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
export interface ArtifactCardProps {
  name: string;
  url: string;
}

const props = defineProps<ArtifactCardProps>();
</script>
