<template>
  <q-page padding>
    <!-- content -->
    <header>
      <span class="text-h3">Edit Model</span>
    </header>
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
            />
            <q-input
              outlined
              v-if="editMetadataStore.experimentPlatform != ''"
              v-model="editMetadataStore.experimentID"
              class="q-ml-md q-pb-xl"
              label="Experiment ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
            <q-select
              outlined
              v-model="editMetadataStore.datasetPlatform"
              class="q-ml-md q-pb-xl"
              :options="creatorPreset.datasetPlatforms"
              label="Dataset Platform (Optional)"
            />
            <q-input
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
            <q-btn
              label="Populate card description"
              rounded
              color="secondary"
              @click="popupContent = true"
            />

            <tiptap-editor
              editable
              :content="editMetadataStore.markdownContent"
              :replace-content="replaceContent"
              @update:content="editMetadataStore.markdownContent = $event"
              @replaced-content="replaceContent = false"
            />
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
              :content="editMetadataStore.performanceMarkdown"
              @update:content="editMetadataStore.performanceMarkdown = $event"
            />
          </div>
        </div>
      </q-step>
    </q-stepper>
  </q-page>
</template>

<script setup lang="ts">
import { Ref, ref } from 'vue';
import { useModelStore } from 'src/stores/model-store';
import { useEditMetadataStore } from 'src/stores/edit-metadata-store';
import { useCreationPreset } from 'src/stores/creation-preset';

// Initialize with data from model
const editMetadataStore = useEditMetadataStore();
const creatorPreset = useCreationPreset();
</script>
