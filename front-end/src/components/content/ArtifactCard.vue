<template>
  <q-card>
    <q-card-section>
      <div class="text-h6">{{ props.artifact.name }}</div>
      <q-badge
        :label="props.artifact.artifactType"
        color="secondary"
        text-color="surface"
        rounded
      ></q-badge>
    </q-card-section>
    <q-separator></q-separator>
    <q-card-actions>
      <q-chip
        text-color="surface"
        color="primary"
        icon="content_copy"
        :label="props.artifact.url"
        clickable
        @click="copyURL"
      ></q-chip>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { copyToClipboard, Notify } from 'quasar';
import { Artifact } from 'src/stores/model-store';
export interface ArtifactCardProps {
  artifact: Artifact;
}

const props = defineProps<ArtifactCardProps>();

const copyURL = () => {
  copyToClipboard(props.artifact.url)
    .then(() => {
      console.log(`Copy ${props.artifact.url}`);
      Notify.create({
        message: 'Copied artifact link to clipboard',
        color: 'positive',
      });
    })
    .catch((err) => {
      console.error(err);
    });
};
</script>
