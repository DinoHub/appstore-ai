<template>
  <q-page padding>
    <!-- content -->
    <header class="row q-py-md">
      <div class="col-12 col-sm-8 text-h3">
        {{ model.title }}
      </div>
      <!-- <div class="col-12 col-sm-4 self-center text-right">
        <q-btn
          rounded
          no-caps
          disable
          label="Perform Transfer Learning"
          color="primary"
        ></q-btn>
      </div> -->
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
      <section class="col-12 col-sm-8 q-px-lg q-py-md">
        <tiptap-display :content="model.markdown"></tiptap-display>
        <tiptap-display :content="model.performance"></tiptap-display>
      </section>
      <aside class="col-12 col-sm-4">
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
              no-caps
            ></q-tab>
            <q-tab
              v-if="model.videoLocation"
              name="video"
              label="Video"
              no-caps
            ></q-tab>
            <q-tab name="metadata" label="Metadata" no-caps></q-tab>
            <q-tab
              name="artifacts"
              label="Artifacts"
              v-if="model.artifacts.length"
              no-caps
            ></q-tab>
            <q-tab
              v-if="isModelOwner"
              name="manage"
              label="Manage"
              no-caps
            ></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab" animated keep-alive>
            <q-tab-panel v-if="model.inferenceServiceName" name="inference">
              <gradio-frame
                :url="inferenceUrl ?? ''"
                :status="inferenceStatus"
                :debug-mode="isModelOwner"
                v-if="inferenceStatus !== undefined"
              ></gradio-frame>
              <q-card v-else>
                <q-card-section>
                  <div class="text-h6 text-center">
                    <q-icon name="warning" color="warning" />
                    {{
                      serviceHealthy
                        ? 'Service is unavailable at the moment.'
                        : 'Service is down or not found.'
                    }}
                  </div>
                  <div v-if="serviceHealthy">
                    <div class="text-center">
                      <q-btn
                        class="q-my-md"
                        rounded
                        no-caps
                        padding="sm xl"
                        label="View Status (Debug)"
                        @click="showDetailedStatus = true"
                      />
                    </div>
                    <p>This may be due to one of the following reasons:</p>
                    <ol>
                      <li>
                        The service is still being created (e.g pulling in
                        image).
                      </li>
                      <li>
                        The service is unable to be spun up due to a lack of
                        resources
                      </li>
                      <li>
                        The service container is unable to properly startup
                      </li>
                    </ol>
                  </div>
                  <div v-else>
                    <p>This may be due to one of the following reasons:</p>
                    <ol>
                      <!-- Currently only unhealthy if status endpoint returns 404 -->
                      <li>The service has been removed from the cluster.</li>
                      <li>The service has been renamed.</li>
                    </ol>
                  </div>
                </q-card-section>
                <q-card-actions>
                  <q-btn
                    v-if="!serviceHealthy"
                    rounded
                    no-caps
                    padding="sm xl"
                    label="Repair Instance"
                    @click="restoreService"
                    class="q-mx-auto"
                  ></q-btn>
                  <!-- Move this to manage -->
                </q-card-actions>
              </q-card>
            </q-tab-panel>
            <q-tab-panel v-if="model.videoLocation" name="video">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Video Preview</div>
                </q-card-section>
                <q-separator></q-separator>
                <q-card-actions class="justify-center">
                  <vue-plyr playsinline>
                    <video controls playsinline>
                      <source :src="model.videoLocation" />
                    </video>
                  </vue-plyr>
                </q-card-actions>
              </q-card>
            </q-tab-panel>
            <q-tab-panel name="metadata">
              <q-markup-table wrap-cells>
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
                  <tr v-if="model.experiment?.connector">
                    <td>Experiment Platform</td>
                    <td>{{ model.experiment.connector }}</td>
                  </tr>
                  <tr v-if="model.experiment?.experimentId">
                    <td>Experiment ID</td>
                    <td>
                      {{ model.experiment.experimentId }}
                    </td>
                  </tr>
                  <tr v-if="model.experiment?.outputUrl">
                    <td>Experiment URL</td>
                    <td>
                      <a :href="model.experiment.outputUrl">
                        {{ model.experiment.outputUrl }}</a
                      >
                    </td>
                  </tr>
                  <tr>
                    <td>Description</td>
                    <td>{{ model.description }}</td>
                  </tr>
                  <tr>
                    <td>Explanation</td>
                    <td>
                      {{ model.explanation }}
                    </td>
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
              <artifact-card
                v-for="artifact in model.artifacts"
                v-bind:key="artifact.name"
                :name="artifact.name"
                :url="artifact.url"
                class="q-mb-md"
              ></artifact-card>
            </q-tab-panel>
            <q-tab-panel v-if="isModelOwner" name="manage">
              <div class="text-h6">Manage your model</div>

              <div class="q-py-md">
                <q-btn
                  label="Edit Model Card Metadata"
                  :to="`/model/${userId}/${modelId}/edit/metadata`"
                  rounded
                  color="secondary"
                  no-caps
                  padding="sm xl"
                ></q-btn>
              </div>
              <div
                class="q-py-md"
                v-if="model.task !== 'Reinforcement Learning'"
              >
                <q-btn
                  :label="
                    model.inferenceServiceName
                      ? 'Edit Model Inference Service'
                      : 'Create Model Inference Service'
                  "
                  :to="`/model/${userId}/${modelId}/edit/inference`"
                  rounded
                  color="tertiary"
                  no-caps
                  padding="sm xl"
                ></q-btn>
              </div>
              <div
                class="q-py-md"
                v-if="model.task === 'Reinforcement Learning'"
              >
                <q-btn
                  :label="
                    model.videoLocation
                      ? 'Edit Example Video'
                      : 'Upload Example Video'
                  "
                  :to="`/model/${userId}/${modelId}/edit/video`"
                  rounded
                  color="tertiary"
                  no-caps
                  padding="sm xl"
                ></q-btn>
              </div>
              <div>
                <!--
                  TODO: this currently only calls delete model endpoint.
                  Right now, the delete model endpoint will add the
                  clear orphaned services task that will run afterwards,
                  but we should probably expicitly call the delete service
                  endpoint here as well instead of relying on what is
                  effectively a side effect.
                -->
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
                    rounded
                    label="Delete"
                    type="submit"
                    color="error"
                    :disable="confirmId !== confirmDeleteLabel"
                    no-caps
                    padding="sm xl"
                  ></q-btn>
                </q-form>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </div>
      </aside>
    </main>
    <aside>
      <q-dialog v-model="showDetailedStatus" persistent>
        <q-card>
          <q-card-section>
            <service-status-display
              :status="inferenceServiceStore.currentServiceStatus"
            >
            </service-status-display>
          </q-card-section>
          <q-card-actions>
            <q-btn
              rounded
              no-caps
              padding="sm xl"
              v-close-popup
              label="Close"
            ></q-btn>
          </q-card-actions>
        </q-card>
      </q-dialog>
    </aside>
  </q-page>
</template>

<style>
.plyr--video {
  width: 100%;
}
</style>
<script setup lang="ts">
import {
  ModelCard,
  LinkedExperiment,
  LinkedDataset,
} from 'src/stores/model-store';
import MaterialChip from 'src/components/content/MaterialChip.vue';
import GradioFrame from 'src/components/content/GradioFrame.vue';
import ArtifactCard from 'src/components/content/ArtifactCard.vue';
import TiptapDisplay from 'src/components/content/TiptapDisplay.vue';
import ServiceStatusDisplay from 'src/components/content/ServiceStatusDisplay.vue';
import { computed, reactive, ref, Ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useModelStore } from 'src/stores/model-store';
import { useRoute, useRouter } from 'vue-router';
import { useExperimentStore } from 'src/stores/experiment-store';
import {
  InferenceServiceStatus,
  useInferenceServiceStore,
} from 'src/stores/inference-service-store';
import { Notify } from 'quasar';

enum Tabs {
  inference = 'inference',
  video = 'video',
  metadata = 'metadata',
  artifacts = 'artifacts',
  manage = 'manage',
}

const route = useRoute();
const router = useRouter();
const modelId = route.params.modelId as string;
const userId = route.params.userId as string;
const tab: Ref<Tabs> = ref(Tabs.inference);
const inferenceUrl: Ref<string | null> = ref(null);
const inferenceStatus: Ref<InferenceServiceStatus | undefined> = ref();
const serviceHealthy = ref(true);
const showDetailedStatus = ref(false);
const authStore = useAuthStore();
const expStore = useExperimentStore();
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
  videoLocation: '',
  markdown: '',
  performance: '',
  created: '',
  lastModified: '',
  artifacts: [],
  description: '',
  explanation: '',
  usage: '',
  limitations: '',
  experiment: {} as LinkedExperiment,
  dataset: {} as LinkedDataset,
}) as ModelCard;

modelStore
  .getModelById(userId, modelId)
  .then((card) => {
    Object.assign(model, card);
    console.log(model);
    // set up datetime to appear nicer in the frontend
    var dateCreated = new Date(model.created);
    var dateLastModified = new Date(model.lastModified);
    model.created = `${dateCreated.getDate()}/${
      dateCreated.getMonth() + 1
    }/${dateCreated.getFullYear()}, ${dateCreated.toLocaleTimeString()}`;
    model.lastModified = `${dateLastModified.getDate()}/${
      dateLastModified.getMonth() + 1
    }/${dateLastModified.getFullYear()}, ${dateLastModified.toLocaleTimeString()}`;
    if (model.experiment != undefined) {
      model.experiment.connector = expStore.experimentConnectors.find(
        (o) => o.value == model.experiment.connector
      ).label;
    }
    if (!model.inferenceServiceName && !model.videoLocation) {
      tab.value = Tabs.metadata; // if both not available, go to metadata
      return;
    }
    if (!model.inferenceServiceName) {
      tab.value = Tabs.video; // if inference not available, go to videos tab instead
      return;
    }
    inferenceServiceStore
      .getServiceByName(model.inferenceServiceName)
      .then((service) => {
        inferenceServiceStore
          .getServiceReady(service.serviceName)
          .then((status) => {
            if (!status.ready) {
              Notify.create({
                message: 'Inference service is down',
                color: 'negative',
              });
              return Promise.reject('Inference service is down');
            }
            inferenceUrl.value = service.inferenceUrl;
            inferenceStatus.value = status;
          })
          .catch((err) => {
            if (err === 404) {
              serviceHealthy.value = false;
              Notify.create({
                message:
                  'Inference service is down or not found inside cluster',
                color: 'negative',
              });
            }
          });
      })
      .catch((err) => {
        Notify.create({
          message: err,
          color: 'negative',
        });
        console.error(err);
      });
  })
  .catch((err) => {
    Notify.create({
      message: 'Failed to retrieve model card information',
      color: 'negative',
    });
    console.error(err);
  });

const isModelOwner = computed(() => {
  return model.creatorUserId == authStore.user?.userId;
});

const confirmDeleteLabel = computed(() => {
  return `${userId}/${modelId}`;
});

const confirmId: Ref<string> = ref('');

const restoreService = () => {
  if (!model.inferenceServiceName) {
    Notify.create({
      message: 'No inference service to restore',
      color: 'negative',
    });
    return;
  }
  inferenceServiceStore
    .restoreService(model.inferenceServiceName)
    .then(() => {
      // Attempt to get the service again
      Notify.create({
        message: 'Inference service restored',
        color: 'positive',
      });
      inferenceServiceStore
        .getServiceReady(model.inferenceServiceName)
        .then(() => {
          router.go(0);
        });
    })
    .catch((err) => {
      Notify.create({
        message: err,
        color: 'negative',
      });
      console.error(err);
    });
};
</script>
