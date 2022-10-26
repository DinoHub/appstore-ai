<template>
  <q-page padding>
    <!-- content -->
    <header class="row justify-between q-py-md">
      <div class="col-12 col-sm-8 text-h3">
        {{ model.title }}
      </div>
      <div class="col-12 col-sm-4 self-center">
        <q-btn label="Perform Transfer Learning" color="primary"></q-btn>
      </div>
    </header>
    <aside class="row q-py-sm">
      <q-chip :label="tag" v-for="tag in model.tags" v-bind:key="tag"></q-chip>
    </aside>
    <q-separator></q-separator>
    <main class="row">
      <section class="col col-sm-8">
        <markdown-display :markdown="model.description"></markdown-display>
        <markdown-display :markdown="model.performance"></markdown-display>
      </section>
      <aside class="col col-sm-4">
        <div class="q-gutter-y-md">
          <q-tabs
            v-model="tab"
            dense
            class="text-grey"
            active-color="primary"
            indicator-color="primary"
            align="justify"
          >
            <q-tab name="inference" label="Inference"></q-tab>
            <q-tab name="metadata" label="Metadata"></q-tab>
            <q-tab name="artifacts" label="Artifacts"></q-tab>
            <q-tab v-if="isModelOwner" name="manage" label="Manage"></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab" animated>
            <q-tab-panel name="inference">
              <!-- TODO: Add Gradio iframe here-->
              <iframe src="www.google.com"></iframe>
            </q-tab-panel>
            <q-tab-panel name="metadata">
              <q-markup-table>
                <thead>
                  <tr>
                    <th colspan="2">Metadata</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Created</td>
                    <td><!-- TODO: Get creation and last modified date--></td>
                  </tr>
                  <tr>
                    <td>Last Modified</td>
                    <td><!-- TODO: Get creation and last modified date--></td>
                  </tr>
                  <tr v-if="model.pointOfContact">
                    <td>Point of Contact</td>
                    <td>{{ model.pointOfContact }}</td>
                  </tr>
                  <tr v-if="model.owner">
                    <td>Model Owner</td>
                    <td>{{ model.owner }}</td>
                  </tr>
                  <tr>
                    <td>Model Creator</td>
                    <td>{{ model.creator }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </q-tab-panel>
            <q-tab-panel name="artifacts">
              <!-- TODO -->
            </q-tab-panel>
            <q-tab-panel v-if="isModelOwner" name="manage">
              <!-- TODO: add check that user is model owner-->
            </q-tab-panel>
          </q-tab-panels>
        </div>
      </aside>
    </main>
  </q-page>
</template>

<script setup lang="ts">
import { ModelCard } from 'src/stores/model-store';
import MarkdownDisplay from 'src/components/MarkdownDisplay.vue';
import { computed, reactive, ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';

const tab = ref('inference');
const authStore = useAuthStore();

const model = reactive({
  modelId: 'ModelX',
  title: 'Title',
  task: 'Image Classification',
  tags: ['Tag 1', 'Tag 2', 'tag me'],
  creator: 'Panda',
  inferenceApi: 'localhost:5151',
  description: 'This model does blah blah blah.\n## Model Use\n....',
  performance: '## Performance\n|Metric|Value|\n|---|---|\n|F1|0.9|',
}) as ModelCard;

const isModelOwner = computed(() => {
  return model.creator == authStore.user?.userId;
});
</script>
