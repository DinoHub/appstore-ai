<template>
  <div class="q-pa-md col-9">
    <q-stepper
      v-model="creationStore.step"
      ref="stepper"
      animated
      done-color="secondary"
      error-color="red"
      active-color="primary"
      class="shadow-0 justify-center text-center full-height"
      header-class="no-border q-px-xl"
    >
      <q-step
        :name="1"
        title="Links"
        icon="link"
        :done="
          creationStore.modelPath != '' &&
          (creationStore.experimentID != '' ||
            creationStore.experimentPlatform == '') &&
          (creationStore.datasetID != '' || creationStore.datasetPlatform == '')
        "
        :error="
          creationStore.modelPath == '' ||
          (creationStore.experimentID == '' &&
            creationStore.experimentPlatform != '') ||
          (creationStore.datasetID == '' && creationStore.datasetPlatform != '')
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-4 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Links</h6>
            <q-input
              v-model="creationStore.modelPath"
              class="q-ml-md q-pb-xl"
              hint="Model Path"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <q-select
              v-model="creationStore.experimentPlatform"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.experimentPlatforms"
              hint="Experiment Platform (Optional)"
            />
            <q-input
              v-if="creationStore.experimentPlatform != ''"
              v-model="creationStore.experimentID"
              class="q-ml-md q-pb-xl"
              hint="Experiment ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
            <q-select
              v-model="creationStore.datasetPlatform"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.datasetPlatforms"
              hint="Dataset Platform (Optional)"
            />
            <q-input
              v-if="creationStore.datasetPlatform != ''"
              v-model="creationStore.datasetID"
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
          creationStore.modelName != '' &&
          creationStore.modelTask != '' &&
          creationStore.tags.length > 0 &&
          creationStore.frameworks.length > 0
        "
        :error="
          creationStore.modelName == '' ||
          creationStore.modelTask == '' ||
          creationStore.tags.length <= 0 ||
          creationStore.frameworks.length <= 0
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-3 q-pr-md q-mr-xl shadow-2 rounde">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Information</h6>
            <q-input
              v-model="creationStore.modelName"
              class="q-ml-md q-pb-xl"
              hint="Model Name"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              reactive-rules
            ></q-input>
            <q-select
              v-model="creationStore.modelTask"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.tasksList"
              hint="Task"
              :rules="[(val) => !!val || 'Field is required']"
            />
          </div>
          <div class="col-3 q-mx-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Tags</h6>
            <q-select
              hint="Tags"
              v-model="creationStore.tags"
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
              hint="Frameworks"
              v-model="creationStore.frameworks"
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
          <div class="col-3 q-pl-md q-ml-xl shadow-2 rounded">
            <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
            <q-input
              v-model="creationStore.modelOwner"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Model Owner (Optional)"
            ></q-input>
            <q-input
              v-model="creationStore.modelPOC"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Point of Contact (Optional)"
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="3"
        title="Model Description"
        icon="person"
        :done="
          creationStore.modelDesc != '' &&
          creationStore.modelExplain != '' &&
          creationStore.modelUsage != '' &&
          creationStore.modelLimitations != ''
        "
        :error="
          creationStore.modelDesc == '' ||
          creationStore.modelExplain == '' ||
          creationStore.modelUsage == '' ||
          creationStore.modelLimitations == ''
        "
      >
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Description</h6>
            <q-input
              v-model="creationStore.modelDesc"
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
              v-model="creationStore.modelExplain"
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
              v-model="creationStore.modelUsage"
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
              v-model="creationStore.modelLimitations"
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
          creationStore.markdownContent.includes('(Example Text to Replace)') ==
          false
        "
        :error="
          creationStore.markdownContent.includes('(Example Text to Replace)') !=
          false
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
                creationStore.markdownContent.includes(
                  '(Example Text to Replace)'
                ) != false
              "
            >
              <q-icon class="" name="error" size="1.5rem" />
              Please remove the example content and style your own content
            </div>
            <!-- <editor
              v-model="creationStore.markdownContent"
              :init="{
                height: 650,
                plugins:
                  'insertdatetime lists link image table help anchor code codesample charmap advlist',
                toolbar: creatorPreset.markdownToolbar,
                setup: (editor) => {
                  editor.ui.registry.addButton('replaceValues', {
                    text: 'Replace Values',
                    onAction: (api) => {
                      popupContent = true;
                    },
                  });
                },
              }"
            /> -->
            <tiptap-editor :content="creationStore.markdownContent" />
          </div>
        </div>
      </q-step>

      <q-step
        :name="5"
        title="Performance Metrics"
        icon="leaderboard"
        :done="creationStore.step > 4"
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">
              Performance Metrics
            </h6>
            <editor
              v-model="metricsContent"
              :init="{
                height: 600,
                plugins:
                  'insertdatetime lists link image table help anchor code codesample charmap',
              }"
              toolbar="undo redo | blocks | bold italic underline 
              strikethrough | alignleft aligncenter alignright | outdent 
              indent | charmap anchor hr | bullist numlist | insertdatetime graphTinymcePlugin"
            />
          </div>
        </div>
      </q-step>

      <q-step
        :name="6"
        title="Inference Engine"
        icon="code"
        :done="creationStore.step > 6"
        v-if="creationStore.modelTask != 'Reinforcement Learning'"
      >
        <div
          class="row justify-center"
          v-if="
            creationStore.modelTask != 'Reinforcement Learning' &&
            displayImageSubmit == false
          "
        >
          <div class="q-pa-md q-gutter-sm col-4 shadow-1">
            <h6 class="text-left q-mb-md">Setting Up Inference Engine</h6>
            <q-btn
              icon="check"
              color="secondary"
              label="I have set up an Inference Engine API Image"
              no-caps
              align="left"
              class="q-mb-sm float-left"
              style="width: 95.6%"
              unelevated
              @click="
                $refs.stepper.next();
                simulateSubmit();
              "
            />
            <q-btn
              icon="help"
              color="black"
              label="Guide me through the set up process"
              no-caps
              align="left"
              class="float-left"
              style="width: 95.6%"
              unelevated
            />
          </div>
        </div>
      </q-step>

      <q-step :name="7" title="Submission" icon="publish">
        <div
          class="row justify-center"
          v-if="creationStore.modelTask != 'Reinforcement Learning'"
        >
          <div class="q-pa-md q-gutter-sm col-4 shadow-1">
            <h6 class="text-left q-mb-md q-mr-sm">Inference Engine</h6>
            <q-input
              class="q-pb-xl q-mr-sm"
              autogrow
              hint="Image URI"
              v-model="creationStore.inferenceImage"
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <h6 class="text-left text-bold q-mb-sm">Important Note:</h6>
            <p class="text-left">
              Note that the image provided should be an application that can be
              embedded, using Gradio or Streamlit, with input and output already
              defined by you. If unsure please check instructions and examples
              listed under GitHub page.
            </p>
          </div>
        </div>
        <div
          class="row justify-center"
          v-if="creationStore.modelTask == 'Reinforcement Learning'"
        >
          <div class="q-pa-md q-gutter-sm col-5 shadow-1">
            <h6 class="text-left q-mb-sm">
              Reinforcement Learning Example Video
            </h6>
            <span class="text-left">
              As a Reinforcement Learning algorithm showcase requires an
              environment, it may not be possible for a interactable demo to be
              displayed. In substitution, a video can be submitted in it's place
              that shows the agent's performance in the environment.
            </span>
            <p class="text-negative text-italic">
              <q-icon class="" name="priority_high" size="1.5rem" />
              The video should be under 10MB
              <q-icon class="" name="priority_high" size="1.5rem" />
            </p>
            <q-uploader
              class="q-mx-auto"
              url=""
              label="Submit video here"
              accept="video/*"
              max-total-size="10000000"
              @rejected="onRejected"
            />
          </div>
        </div>
      </q-step>
      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row justify-center">
            <div class="text-right col-1">
              <q-btn
                color="red"
                @click="cancel = true"
                label="Cancel"
                class="q-mr-md"
                :disable="buttonDisable"
              />
            </div>
            <div class="text-right col-6">
              <q-btn
                v-if="creationStore.step > 1"
                color="primary"
                @click="
                  $refs.stepper.previous();
                  simulateSubmit();
                "
                label="Back"
                class="q-mr-md"
                :disable="buttonDisable"
              />
              <q-btn
                v-if="creationStore.step < 6"
                @click="
                  $refs.stepper.next();
                  simulateSubmit();
                "
                color="primary"
                label="Continue"
                :disable="buttonDisable"
              />

              <q-btn
                v-if="
                  creationStore.step == 7 && creationStore.inferenceImage != ''
                "
                @click="submitImage()"
                color="primary"
                label="Submit Image"
                :disable="buttonDisable"
              />
            </div>
          </div>
        </q-stepper-navigation>
      </template>
    </q-stepper>
    <dialog>
      <q-dialog v-model="cancel">
        <q-card>
          <q-card-section>
            <div class="text-h6">Quit</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Are you sure you want to exit the model creation process?
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="red" v-close-popup />
            <q-space />
            <q-btn flat label="Save & Quit" color="green" v-close-popup />
            <q-btn flat label="Quit" color="primary" v-close-popup to="/" />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog v-model="cancel" persistent>
        <q-card>
          <q-card-section>
            <div class="text-h6">Quit</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Are you sure you want to exit the model creation process? <br />
            <span class="text-bold"
              >(Saving will override any previous creations)</span
            >
          </q-card-section>
          <q-card-actions align="right">
            <q-btn flat label="Cancel" color="red" v-close-popup />
            <q-space />
            <q-btn
              flat
              label="Save & Quit"
              color="green"
              to="/"
              v-close-popup
              v-if="localStorage.getItem(creationStore.$id) !== null"
            />
            <q-btn
              flat
              label="Quit"
              color="primary"
              v-close-popup
              to="/"
              @click="flushCreator()"
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
            <q-btn flat label="No" color="red" v-close-popup />
            <q-btn
              flatv
              label="Replace"
              color="primary"
              v-close-popup
              @click="populateEditor(creationStore)"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
      <q-dialog v-model="prevSave" persistent>
        <q-card>
          <q-card-section>
            <div class="text-h6">Previous Draft</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            There was a previous draft found, continue editing draft or delete?
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              flat
              label="Delete"
              color="red"
              v-close-popup
              @click="flushCreator()"
            />
            <q-btn flat label="Continue" color="primary" v-close-popup />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { useExpStore } from 'src/stores/exp-store';
import { useCreationStore } from 'src/stores/creation-store';
import { useCreationPreset } from 'src/stores/creation-preset';
import { ref } from 'vue';
/* Import TinyMCE */
import tinymce from 'tinymce';

import 'tinymce/tinymce';
import 'tinymce/icons/default/icons';
import 'tinymce/themes/silver/theme';
import 'tinymce/models/dom/model';
import 'tinymce/skins/ui/tinymce-5/skin.css';
import contentUiCss from 'tinymce/skins/ui/tinymce-5/content.css';
import contentCss from 'tinymce/skins/content/default/content.css';
/* Import plugins */
import 'tinymce/plugins/image';
import 'tinymce/plugins/help';
import 'tinymce/plugins/insertdatetime';
import 'tinymce/plugins/codesample';
import 'tinymce/plugins/charmap';
import 'tinymce/plugins/anchor';
import 'tinymce/plugins/advlist';
import 'tinymce/plugins/code';
import 'tinymce/plugins/emoticons';
import 'tinymce/plugins/emoticons/js/emojis';
import 'tinymce/plugins/link';
import 'tinymce/plugins/lists';
import 'tinymce/plugins/table';

// TinyMCE plugins
// https://www.tiny.cloud/docs/tinymce/6/plugins/
import 'src/plugins/tinymce-charts';
import Editor from '@tinymce/tinymce-vue';
import { Cookies } from 'quasar';
import TiptapEditor from './editor/TiptapEditor.vue';

// constants for stores
const expStore = useExpStore();
const creationStore = useCreationStore();
const creatorPreset = useCreationPreset();

// const for checking whether previous saves exist
const prevSave = ref(localStorage.getItem(creationStore.$id) !== null);

// bool for loading state when retrieving experiments
const loadingExp = ref(false);

// variables for performance metrics in model creation
const metricsContent = ref('');

// variables for inference submit
const displayImageSubmit = ref(false);

// variables for popup exits
const cancel = ref(false);
const popupContent = ref(false);
const buttonDisable = ref(false);

// function for triggering events that should happen when next step is triggered
function simulateSubmit() {
  if (
    creationStore.experimentID != '' &&
    creationStore.step == 2 &&
    creationStore.tags.length == 0 &&
    creationStore.frameworks.length == 0
  ) {
    loadingExp.value = true;
    buttonDisable.value = true;
    expStore.getExperimentByID(creationStore.experimentID).then((value) => {
      creationStore.tags = value.tags;
      creationStore.frameworks = value.frameworks;
      loadingExp.value = false;
      buttonDisable.value = false;
    });
  }
  console.log(creationStore.step);
}
function flushCreator() {
  creationStore.$reset();
  localStorage.removeItem(`${creationStore.$id}`);
}
function submitImage() {
  creationStore.launchImage(
    creationStore.inferenceImage,
    Cookies.get('auth').user.userId
  );
}
function finalSubmit() {
  if (creationStore.modelOwner == '') {
    creationStore.modelOwner = authStore.user?.name;
  }
  if (creationStore.modelPOC == '') {
    creationStore.modelPOC = authStore.user?.name;
  }
}

// function for populating editor with values from previous step
function populateEditor(store) {
  store.$patch({
    markdownContent: `
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
  ${store.modelLimitations}
  <p>&nbsp;</p>
  <h3>Limitations <a id="limitations"></a></h3>
  <hr>
  ${store.modelLimitations}
  <p>&nbsp;</p>
  `,
  });
  popupContent.value = false;
}
</script>
