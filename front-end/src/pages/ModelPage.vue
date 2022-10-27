<template>
  <q-page padding>
    <!-- content -->
    <header class="row q-py-md">
      <div class="col-12 col-sm-8 text-h3">
        {{ model.title }}
      </div>
      <div class="col-12 col-sm-4 self-center text-right">
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
            <q-tab
              v-if="model.inferenceApi"
              name="inference"
              label="Inference"
            ></q-tab>
            <q-tab name="metadata" label="Metadata"></q-tab>
            <q-tab name="artifacts" label="Artifacts"></q-tab>
            <q-tab v-if="isModelOwner" name="manage" label="Manage"></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab" animated>
            <q-tab-panel v-if="model.inferenceApi" name="inference">
              <!-- TODO: Add Gradio iframe here-->
              <gradio-frame :url="model.inferenceApi"></gradio-frame>
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
                    <td>{{ model.created }}</td>
                  </tr>
                  <tr>
                    <td>Last Modified</td>
                    <td>{{ model.lastModified }}</td>
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
              Work in Progress
            </q-tab-panel>
            <q-tab-panel v-if="isModelOwner" name="manage">
              <!-- TODO: add check that user is model owner-->
              <div class="text-h6">Manage your model</div>

              <div class="q-py-md">
                <q-btn label="Edit Model Card" color="primary"></q-btn>
              </div>
              <div>
                <q-form
                  @submit="modelStore.deleteModelById(userId, modelId)"
                  class="q-gutter-md"
                >
                  <q-input
                    v-model="confirmId"
                    :hint="`Type ${confirmDeleteLabel} to confirm delete`"
                    lazy-rules
                    :rules="[
                      (val) =>
                        val == confirmDeleteLabel ||
                        `Type ${confirmDeleteLabel} to confirm delete`,
                    ]"
                  >
                  </q-input>
                  <q-btn
                    label="Delete"
                    type="submit"
                    color="negative"
                    :disable="confirmId !== confirmDeleteLabel"
                  ></q-btn>
                </q-form>
              </div>
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
import GradioFrame from 'src/components/GradioFrame.vue';
import { computed, reactive, ref, Ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useModelStore } from 'src/stores/model-store';
import { useRoute } from 'vue-router';

enum Tabs {
  inference = 'inference',
  metadata = 'metadata',
  artifacts = 'artifacts',
  manage = 'manage',
}

const route = useRoute();
const modelId = route.params.modelId as string;
const userId = route.params.userId as string;
const tab: Ref<Tabs> = ref(Tabs.inference);
const authStore = useAuthStore();
const modelStore = useModelStore();

const model = reactive({
  modelId: '',
  title: '',
  task: 'Image ',
  tags: [],
  frameworks: [],
  creator: '',
  inferenceApi: 'https://www.youtube.com/embed/tgbNymZ7vqY',
  description: '# Default',
  performance: '',
  created: Date(),
  lastModified: Date(),
}) as ModelCard;

modelStore.getModelById(userId, modelId).then((card) => {
  Object.assign(model, card);
  if (!model.inferenceApi) {
    tab.value = Tabs.metadata; // if inference not available, hide
  }
});

const isModelOwner = computed(() => {
  return model.creator == authStore.user?.userId;
});

const confirmDeleteLabel = computed(() => {
  return `${userId}/${modelId}`;
});

const confirmId: Ref<string> = ref('');
</script>
