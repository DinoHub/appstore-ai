<template>
  <q-page padding>
    <!-- content -->
    <header class="row q-py-md">
      <div class="col-12 col-sm-8 text-h3">
        {{ model.title }}
      </div>
      <div class="col-12 col-sm-4 self-center text-right">
        <q-btn
          rounded
          label="Perform Transfer Learning"
          color="primary"
        ></q-btn>
      </div>
    </header>
    <aside class="row q-py-sm">
      <material-chip
        :label="model.task"
        type="task"
        clickable
        @click.stop="$router.push(`/models?tasks=${model.task}`)"
      />
      <material-chip
        v-for="tag in model.frameworks"
        :key="tag"
        :label="tag"
        type="framework"
        clickable
        @click.stop="$router.push(`/models?frameworks=${tag}`)"
      >
      </material-chip>
      <material-chip
        v-for="tag in model.tags"
        :key="tag"
        :label="tag"
        type="tag"
        clickable
        @click.stop="$router.push(`/models?tags=${tag}`)"
      >
      </material-chip>
    </aside>
    <q-separator></q-separator>
    <main class="row">
      <section class="col col-sm-8 q-px-lg q-py-md">
        <!-- <markdown-display :markdown="model.description"></markdown-display> -->
        <!-- <markdown-display :markdown="model.performance"></markdown-display> -->
        <tiptap-display :content="model.markdown"></tiptap-display>
        <tiptap-display :content="model.performance"></tiptap-display>
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
              v-if="model.inferenceServiceName"
              name="inference"
              label="Inference"
            ></q-tab>
            <q-tab name="metadata" label="Metadata"></q-tab>
            <q-tab
              name="artifacts"
              label="Artifacts"
              v-if="model.artifacts.length"
            ></q-tab>
            <q-tab v-if="isModelOwner" name="manage" label="Manage"></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab" animated>
            <q-tab-panel v-if="model.inferenceServiceName" name="inference">
              <gradio-frame :url="inferenceUrl"></gradio-frame>
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
                    <td>{{ model.creatorUserId }}</td>
                  </tr>
                  <tr>
                    <td>Description</td>
                    <td>{{ model.description }}</td>
                  </tr>
                  <tr>
                    <td>Explaination</td>
                    <td>{{ model.explanation }}</td>
                  </tr>
                  <tr>
                    <td>Usage</td>
                    <td>{{ model.usage }}</td>
                  </tr>
                  <tr>
                    <td>Limitations</td>
                    <td>{{ model.limitations }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </q-tab-panel>
            <q-tab-panel name="artifacts" v-if="model.artifacts.length">
              <!-- TODO -->
              <artifact-card
                v-for="artifact in model.artifacts"
                v-bind:key="artifact.name"
                :name="artifact.name"
                :url="artifact.url"
              ></artifact-card>
            </q-tab-panel>
            <q-tab-panel v-if="isModelOwner" name="manage">
              <!-- TODO: add check that user is model owner-->
              <div class="text-h6">Manage your model</div>

              <div class="q-py-md">
                <q-btn
                  label="Edit Model Card Metadata"
                  :to="`/model/${userId}/${modelId}/edit`"
                  rounded
                  color="secondary"
                ></q-btn>
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
import MarkdownDisplay from 'src/components/content/MarkdownDisplay.vue';
import MaterialChip from 'src/components/content/MaterialChip.vue';
import GradioFrame from 'src/components/content/GradioFrame.vue';
import ArtifactCard from 'src/components/content/ArtifactCard.vue';
import TiptapEditor from 'src/components/editor/TiptapEditor.vue';
import TiptapDisplay from 'src/components/content/TiptapDisplay.vue';
import { computed, reactive, ref, Ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useModelStore } from 'src/stores/model-store';
import { useRoute } from 'vue-router';
import { useInferenceServiceStore } from 'src/stores/inference-service-store';

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
const inferenceUrl: Ref<string | null> = ref(null);
const authStore = useAuthStore();
const modelStore = useModelStore();
const inferenceServiceStore = useInferenceServiceStore();

const model = reactive({
  modelId: '',
  title: '',
  task: '',
  tags: [],
  frameworks: [],
  creatorUserId: '',
  inferenceServiceName: '',
  markdown: '',
  performance: '',
  created: '',
  lastModified: '',
  artifacts: [],
  description: '',
  explanation: '',
  usage: '',
  limitations: '',
}) as ModelCard;

modelStore.getModelById(userId, modelId).then((card) => {
  Object.assign(model, card);
  if (!model.inferenceServiceName) {
    tab.value = Tabs.metadata; // if inference not available, hide
    return;
  }
  inferenceServiceStore
    .getServiceByName(model.inferenceServiceName)
    .then((service) => {
      inferenceUrl.value = service.inferenceUrl;
    });
});

const isModelOwner = computed(() => {
  return model.creatorUserId == authStore.user?.userId;
});

const confirmDeleteLabel = computed(() => {
  return `${userId}/${modelId}`;
});

const confirmId: Ref<string> = ref('');
</script>
