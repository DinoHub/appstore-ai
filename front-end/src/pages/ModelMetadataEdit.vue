<template>
  <q-page padding>
    <!-- content -->
    <model-card-edit-tabs></model-card-edit-tabs>
    <q-stepper
      v-model="editMetadataStore.step"
      ref="stepper"
      header-nav
      animated
      done-color="primary"
      error-color="error"
      active-color="secondary"
    >
      <q-step
        :name="1"
        title="Links"
        icon="link"
        :done="
          editMetadataStore.modelPath != '' &&
          (editMetadataStore.experimentID != '' ||
            editMetadataStore.experimentPlatform == '') &&
          (editMetadataStore.datasetID != '' ||
            editMetadataStore.datasetPlatform == '')
        "
        :error="
          editMetadataStore.modelPath == '' ||
          (editMetadataStore.experimentID == '' &&
            editMetadataStore.experimentPlatform != '') ||
          (editMetadataStore.datasetID == '' &&
            editMetadataStore.datasetPlatform != '')
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-4 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Links</h6>
            <!-- modelPath? -->
            <q-input
              outlined
              v-model="editMetadataStore.modelPath"
              class="q-ml-md q-pb-xl"
              label="Model Path"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <q-select
              outlined
              v-model="editMetadataStore.experimentPlatform"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.experimentPlatforms"
              label="Experiment Platform (Optional)"
              map-options
              emit-value
            />
            <q-input
              outlined
              v-if="editMetadataStore.experimentPlatform != ''"
              v-model="editMetadataStore.experimentID"
              class="q-ml-md q-pb-xl"
              label="Experiment ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              @update:model-value="
                setStateFromExperimentDetails(editMetadataStore)
              "
              debounce="1000"
            >
            </q-input>
            <q-select
              outlined
              v-model="editMetadataStore.datasetPlatform"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.datasetPlatforms"
              label="Dataset Platform (Optional)"
              map-options
              emit-value
            />
            <q-input
              outlined
              v-if="editMetadataStore.datasetPlatform != ''"
              v-model="editMetadataStore.datasetID"
              class="q-ml-md q-pb-xl"
              hint="Dataset ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="2"
        title="Model & Owner Information"
        icon="person"
        :done="
          editMetadataStore.modelName != '' &&
          editMetadataStore.modelTask != '' &&
          editMetadataStore.tags.length > 0 &&
          editMetadataStore.frameworks.length > 0
        "
        :error="
          editMetadataStore.modelName == '' ||
          editMetadataStore.modelTask == '' ||
          editMetadataStore.tags.length <= 0 ||
          editMetadataStore.frameworks.length <= 0
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col q-pr-md q-mr-xl shadow-2 rounde">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Information</h6>
            <q-input
              outlined
              v-model="editMetadataStore.modelName"
              class="q-ml-md q-pb-xl"
              label="Model Name"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              reactive-rules
            ></q-input>
            <q-select
              outlined
              v-model="editMetadataStore.modelTask"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.tasksList"
              label="Task"
              :rules="[(val) => !!val || 'Field is required']"
            />
          </div>
          <div class="col q-mx-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Tags</h6>
            <q-select
              outlined
              label="Tags"
              v-model="editMetadataStore.tags"
              use-input
              use-chips
              multiple
              autogrow
              hide-dropdown-icon
              input-debounce="0"
              new-value-mode="add-unique"
              :loading="loadingExp"
              class="q-ml-md q-pr-md q-pb-xl"
              :rules="[(val) => val.length >= 1 || 'One or more tags required']"
            />
            <q-select
              outlined
              label="Frameworks"
              v-model="editMetadataStore.frameworks"
              use-input
              use-chips
              multiple
              autogrow
              hide-dropdown-icon
              input-debounce="0"
              new-value-mode="add-unique"
              :loading="loadingExp"
              class="q-ml-md q-pr-md q-pb-xl"
              :rules="[
                (val) => val.length >= 1 || 'One or more frameworks required',
              ]"
            />
          </div>
          <div class="col q-pl-md q-ml-xl shadow-2 rounded">
            <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
            <q-input
              outlined
              v-model="editMetadataStore.modelOwner"
              autogrow
              class="q-mr-md q-pb-xl"
              label="Model Owner (Optional)"
            ></q-input>
            <q-input
              outlined
              v-model="editMetadataStore.modelPOC"
              autogrow
              class="q-mr-md q-pb-xl"
              label="Point of Contact (Optional)"
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="3"
        title="Model Description"
        icon="person"
        :done="
          editMetadataStore.modelDesc != '' &&
          editMetadataStore.modelExplain != '' &&
          editMetadataStore.modelUsage != '' &&
          editMetadataStore.modelLimitations != ''
        "
        :error="
          editMetadataStore.modelDesc == '' ||
          editMetadataStore.modelExplain == '' ||
          editMetadataStore.modelUsage == '' ||
          editMetadataStore.modelLimitations == ''
        "
      >
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Description</h6>
            <q-input
              v-model="editMetadataStore.modelDesc"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Explanation</h6>
            <q-input
              v-model="editMetadataStore.modelExplain"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Usage</h6>
            <q-input
              v-model="editMetadataStore.modelUsage"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Limitations</h6>
            <q-input
              v-model="editMetadataStore.modelLimitations"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="4"
        title="Card Markdown"
        icon="assignment"
        :done="
          editMetadataStore.markdownContent.includes(
            '(Example Text to Replace)',
          ) == false
        "
        :error="
          editMetadataStore.markdownContent.includes(
            '(Example Text to Replace)',
          ) != false
        "
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-ml-md q-mb-sm">Card Markdown</h6>
            <p class="text-left q-ml-md q-mb-sm">
              This is the HTML markdown that will shown in the model page.<br />
              Style it to your liking and display whatever additional
              information you would like, such as tables, lists, code samples or
              images. <br />
              You can follow the example content structure or come up with
              something else.
            </p>
            <div
              class="text-left q-ml-md q-mb-md text-italic text-negative"
              v-if="
                editMetadataStore.markdownContent.includes(
                  '(Example Text to Replace)',
                ) != false
              "
            >
              <q-icon class="" name="error" size="1.5rem" />
              Please remove the example content and style your own content
            </div>
            <!-- Button to populate markdown with text from previous step-->

            <tiptap-editor
              editable
              :content="editMetadataStore.markdownContent"
              :replace-content="replaceContent"
              @update:content="editMetadataStore.markdownContent = $event"
              @replaced-content="replaceContent = false"
            >
              <template #toolbar>
                <q-btn
                  label="Populate card description"
                  rounded
                  no-caps
                  color="secondary"
                  @click="popupContent = true"
                />
              </template>
            </tiptap-editor>
          </div>
        </div>
      </q-step>

      <q-step
        :name="5"
        title="Performance Metrics"
        icon="leaderboard"
        :done="
          editMetadataStore.performanceMarkdown.includes(
            'This is an example graph showcasing how the graph option works! Use the button on the toolbar to create new graphs. You can also edit preexisting graphs using the edit button!',
          ) == false
        "
        :error="
          editMetadataStore.performanceMarkdown.includes(
            'This is an example graph showcasing how the graph option works! Use the button on the toolbar to create new graphs. You can also edit preexisting graphs using the edit button!',
          ) != false
        "
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">
              Performance Metrics
            </h6>
            <p class="text-left q-ml-md q-mb-sm">
              This is a editor section for performance metrics to be inserted.
              <br />
              If a ClearML experiment ID was given, the scalars will be inserted
              here.<br />
              Style the performance metrics and insert any relevant descriptions
              to your liking to let users know the performance of the model.
            </p>
            <div
              class="text-left q-ml-md q-mb-md text-italic text-negative"
              v-if="
                editMetadataStore.performanceMarkdown.includes(
                  'This is an example graph showcasing how the graph option works! Use the button on the toolbar to create new graphs. You can also edit preexisting graphs using the edit button!',
                ) != false
              "
            >
              <q-icon class="" name="error" size="1.5rem" />
              Please remove the example content and style/update with your own
              content
            </div>
            <tiptap-editor
              editable
              :replace-content="replacePerformanceContent"
              @replaced-content="replacePerformanceContent = false"
              :content="editMetadataStore.performanceMarkdown"
              @update:content="editMetadataStore.performanceMarkdown = $event"
            >
              <template #toolbar>
                <q-btn
                  label="Retrieve plots from experiment"
                  rounded
                  no-caps
                  color="secondary"
                  @click="showPlotModal = true"
                  v-if="
                    editMetadataStore.experimentPlatform != '' &&
                    editMetadataStore.experimentID != ''
                  " /></template
            ></tiptap-editor>
          </div>
        </div>
      </q-step>
      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row justify-center">
            <div class="text-right col-1">
              <q-btn
                no-caps
                outline
                rounded
                color="error"
                @click="cancel = true"
                label="Cancel"
                class="q-mr-md"
                padding="sm xl"
                :disable="buttonDisable"
              />
            </div>
            <div class="text-right col-6 q-gutter-md">
              <q-btn
                v-if="editMetadataStore.step > 1"
                color="primary"
                @click="$refs.stepper.previous()"
                no-caps
                outline
                rounded
                label="Back"
                class="q-mr-md"
                padding="sm xl"
                :disable="buttonDisable"
              />
              <q-btn
                v-if="editMetadataStore.step < 5"
                @click="$refs.stepper.next()"
                no-caps
                rounded
                color="primary"
                label="Continue"
                padding="sm xl"
                :disable="buttonDisable"
              />
              <q-btn
                no-caps
                rounded
                @click="saveEdit()"
                color="primary"
                label="Save Edits"
                padding="sm xl"
                :disable="buttonDisable"
              />
            </div>
          </div>
        </q-stepper-navigation>
      </template>
    </q-stepper>
    <dialog>
      <q-dialog v-model="cancel" persistent>
        <q-card>
          <q-card-section>
            <div class="text-h6">Quit</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Are you sure you want to exit the model creation process? <br />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              rounded
              outline
              label="Cancel"
              padding="sm xl"
              color="error"
              v-close-popup
            />
            <q-space />
            <q-btn
              rounded
              label="Quit"
              color="primary"
              padding="sm xl"
              to="/"
              v-close-popup
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog v-model="popupContent">
        <q-card>
          <q-card-section>
            <div class="text-h6">Markdown</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Replace example content with your own values?
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              outline
              rounded
              label="No"
              color="error"
              padding="sm xl"
              v-close-popup
            />
            <q-btn
              rounded
              padding="sm xl"
              label="Replace"
              color="primary"
              v-close-popup
              @click="populateEditor(editMetadataStore)"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog v-model="showPlotModal" persistent>
        <q-card>
          <q-card-section>
            <div class="text-h6">Retrieve Experiment Plots</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Retrieve any plots from your experiment?
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              outline
              rounded
              no-caps
              label="No"
              color="error"
              padding="sm xl"
              v-close-popup
              :disable="buttonDisable"
            />
            <q-btn
              rounded
              no-caps
              padding="sm xl"
              label="Add plots"
              color="primary"
              @click="addExpPlots(editMetadataStore)"
              :disable="buttonDisable"
            />
          </q-card-actions>
          <q-inner-loading :showing="buttonDisable">
            <q-spinner-gears size="50px" color="primary" />
          </q-inner-loading>
        </q-card>
      </q-dialog>
    </dialog>
  </q-page>
</template>

<script setup lang="ts">
// TODO: Refactor model creation and editing code
// as the way it is currently handled is not ideal
// e.g. Repetitive Code
import { onMounted, Ref, ref } from 'vue';
import { watchDebounced } from '@vueuse/core';
import { useAuthStore } from 'src/stores/auth-store';
import { Notify } from 'quasar';
import { useExpStore } from 'src/stores/exp-store';
import { useEditMetadataStore } from 'src/stores/edit-model-metadata-store';
import { useCreationPreset } from 'src/stores/creation-preset';
import { useRoute, useRouter } from 'vue-router';

import TiptapEditor from 'src/components/editor/TiptapEditor.vue';
import ModelCardEditTabs from 'src/components/layout/ModelCardEditTabs.vue';

const emit = defineEmits(['update-exp']);

// Initialize with data from model
const editMetadataStore = useEditMetadataStore();
const experimentStore = useExpStore();
const creatorPreset = useCreationPreset();
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const modelId = route.params.modelId as string;

// bool for loading state when retrieving experiments
const loadingExp = ref(false);
const replaceContent: Ref<boolean> = ref(false); // indicator to replace content with model desc data
const replacePerformanceContent: Ref<boolean> = ref(false); // indicator to replace content with model desc data

// variables for popup exits
const cancel = ref(false);
const popupContent = ref(false);
const showPlotModal = ref(false);
const buttonDisable = ref(false);

async function checkMetadata(reference) {
  const metadataIsDone = editMetadataStore.checkMetadataValues();
  if ((await metadataIsDone) == true) {
    reference.next();
  } else {
    Notify.create({
      message: 'Enter all values into required fields first before proceeding',
      position: 'top',
      icon: 'warning',
      color: 'negative',
      actions: [
        {
          label: 'Dismiss',
          color: 'white',
          handler: () => {
            /* ... */
          },
        },
      ],
    });
  }
}
function saveEdit() {
  if (authStore.user?.name) {
    if (editMetadataStore.modelOwner == '') {
      editMetadataStore.modelOwner = authStore.user.name;
    }
    if (editMetadataStore.modelPOC == '') {
      editMetadataStore.modelPOC = authStore.user.name;
    }
  }
  editMetadataStore
    .submitEdit(modelId)
    .then(
      // Redirect to model page
      () => {
        Notify.create({
          message: 'Model successfully edited',
          position: 'bottom',
          icon: 'check',
          color: 'primary',
          actions: [
            {
              label: 'Dismiss',
              color: 'white',
              handler: () => {
                /* ... */
              },
            },
          ],
        });
        editMetadataStore.$reset();
        localStorage.removeItem(`${editMetadataStore.$id}`);
        router.push(`/model/${authStore.user?.userId}/${modelId}`);
      },
    )
    .catch(() => {
      Notify.create({
        message: 'Error editing model',
        position: 'bottom',
        icon: 'warning',
        color: 'negative',
        actions: [
          {
            label: 'Dismiss',
            color: 'white',
            handler: () => {
              /* ... */
            },
          },
        ],
      });
    });
}

function populateEditor(store: typeof editMetadataStore) {
  replaceContent.value = true;
  (store.markdownContent = `
  <h3>Description <a id="description"></a></h3>
  <hr>
  ${store.modelDesc}
  <p>&nbsp;</p>
  <h3>Explanation <a id="explanation"></a></h3>
  <hr>
  ${store.modelExplain}
  <p>&nbsp;</p>
  <h3>Model Usage <a id="model_use"></a></h3>
  <hr>
  ${store.modelUsage}
  <p>&nbsp;</p>
  <h3>Limitations <a id="limitations"></a></h3>
  <hr>
  ${store.modelLimitations}
  <p>&nbsp;</p>
  `),
    (popupContent.value = false);
}

function setStateFromExperimentDetails(state: typeof editMetadataStore) {
  if (state.experimentID) {
    experimentStore
      .getExperimentByID(state.experimentID)
      .then((data) => {
        editMetadataStore.tags = Array.from(
          new Set([...editMetadataStore.tags, ...data.tags]),
        );
        editMetadataStore.frameworks = Array.from(
          new Set([...editMetadataStore.frameworks, ...data.frameworks]),
        );
      })
      .catch((err) => {
        console.error('Failed to retrieve experiment details');
        console.error(err);
      });
  }
}

function addExpPlots(store: typeof editMetadataStore) {
  buttonDisable.value = true;
  let newPerformance = store.performanceMarkdown;
  if (store.experimentID) {
    experimentStore
      .getExperimentByID(store.experimentID, true)
      .then((data) => {
        editMetadataStore.plots = [
          ...(data.plots ?? []),
          ...(data.scalars ?? []),
        ];
      })
      .then(() => {
        for (const chart of store.plots) {
          try {
            newPerformance += `
          <p></p><chart data-layout="${JSON.stringify(chart.layout).replace(
            /["]/g,
            '&quot;',
          )}" data-data="${JSON.stringify(chart.data).replace(
            /["]/g,
            '&quot;',
          )}"></chart>
          <p></p>
        `;
          } catch (err) {
            console.log('Failed to retrieve chart');
            continue;
          }
        }
        replacePerformanceContent.value = true;
        store.performanceMarkdown = newPerformance;
        showPlotModal.value = false;
        buttonDisable.value = false;
      })
      .catch((err) => {
        buttonDisable.value = false;
        Notify.create({
          message: 'Failed to insert plots',
          color: 'error',
        });
      });
  }
}

onMounted(() => {
  editMetadataStore.loadFromMetadata(modelId);
});
</script>
