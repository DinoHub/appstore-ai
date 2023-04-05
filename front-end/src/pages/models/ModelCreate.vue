<template>
  <q-page padding>
    <q-stepper
      v-model="creationStore.step"
      ref="stepper"
      animated
      done-color="primary"
      error-color="error"
      active-color="secondary"
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
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Links</h6>
            <p class="text-left q-ml-md q-mb-lg">
              To start, please provide us with some metadata about your model,
              such as the URL to the model (e.g a Git Repository), and any
              experiment or dataset that you would like to associate with it.
            </p>
            <q-input
              outlined
              v-model="creationStore.modelPath"
              class="q-ml-md q-pb-xl"
              label="Model URL"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <span class="text-h6 text-left q-ml-md q-mb-sm"
              >Linked Experiments & Datasets</span
            >
            <p class="text-left q-ml-md q-mb-lg">
              When you supply us with a linked experiment, we will automatically
              retrieve data from the experiment and populate the model card
              fields with them.
            </p>
            <q-select
              outlined
              v-model="creationStore.experimentPlatform"
              class="q-ml-md q-pb-xl"
              :options="experimentStore.experimentConnectors"
              label="Experiment Platform (Optional)"
              emit-value
              map-options
            />
            <!-- Dynamic append platform name to label -->
            <q-input
              outlined
              v-if="creationStore.experimentPlatform != ''"
              v-model="creationStore.experimentID"
              class="q-ml-md q-pb-xl"
              :label="`${
                experimentStore.experimentConnectors.find(
                  (connector) =>
                    connector.value === creationStore.experimentPlatform,
                )?.label + ' ' ?? ''
              }Experiment ID`"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              @update:model-value="retrieveExperimentDetails()"
              debounce="2000"
            >
            </q-input>
            <q-select
              outlined
              v-model="creationStore.datasetPlatform"
              class="q-ml-md q-pb-xl"
              :options="datasetStore.datasetConnectors"
              label="Dataset Platform (Optional)"
              emit-value
              map-options
            />
            <q-input
              outlined
              v-if="creationStore.datasetPlatform != ''"
              v-model="creationStore.datasetID"
              class="q-ml-md q-pb-xl"
              :label="`${
                datasetStore.datasetConnectors.find(
                  (connector) =>
                    connector.value === creationStore.datasetPlatform,
                )?.label + ' ' ?? ''
              }Dataset ID`"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              debounce="2000"
              @update:model-value="retrieveDatasetDetails()"
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
          <div class="col q-pr-md q-mr-xl shadow-2 rounde">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Information</h6>
            <q-input
              outlined
              v-model="creationStore.modelName"
              class="q-ml-md q-pb-xl"
              label="Model Name"
              autogrow
              :rules="[
                (val) => !!val || 'Field is required',
                (val) =>
                  val.length <= 50 || 'Please use a maximum of 50 characters',
              ]"
              reactive-rules
            ></q-input>
            <q-select
              outlined
              v-model="creationStore.modelTask"
              class="q-ml-md q-pb-xl"
              :options="modelStore.tasks"
              label="Task"
              :rules="[(val) => !!val || 'Field is required']"
            />
          </div>
          <div class="col q-mx-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Tags</h6>
            <q-select
              outlined
              label="Tags"
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
              placeholder="e.g. Image Classification"
              hint="Press enter to add a new tag"
            />
            <q-select
              outlined
              label="Frameworks"
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
              placeholder="e.g. PyTorch"
              hint="Press enter to add a new framework"
            />
          </div>
          <div class="col q-pl-md q-ml-xl shadow-2 rounded">
            <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
            <q-input
              outlined
              v-model="creationStore.modelOwner"
              autogrow
              class="q-mr-md q-pb-xl"
              label="Model Owner (Optional)"
              hint="This is the person in charge of the model."
            ></q-input>
            <q-input
              outlined
              v-model="creationStore.modelPOC"
              autogrow
              class="q-mr-md q-pb-xl"
              label="Point of Contact (Optional)"
              hint="This is the person to contact for enquiries on the model."
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="3"
        title="Model Card Attributes"
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
        <q-card>
          <q-card-section>
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">
              Model Card Attributes
            </h6>
            <p class="text-left q-mt-md q-ml-md q-mb-sm">
              As part of the model card creation process, we'll need you to
              write out some information pertaining to the model in the below
              sections. As this information is to be stored in a human-readable
              format, any images, tables, or other data should be included in
              the next part of the model card creation process.
            </p>
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Description</h6>
            <q-input
              outlined
              v-model="creationStore.modelDesc"
              class="q-ml-md q-mb-lg"
              type="textarea"
              placeholder="This is a model that does X, Y, Z."
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Explanation</h6>
            <q-input
              outlined
              placeholder="This model works by doing..."
              v-model="creationStore.modelExplain"
              class="q-ml-md q-mb-lg"
              type="textarea"
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Usage</h6>
            <q-input
              v-model="creationStore.modelUsage"
              placeholder="This model can be used for..."
              class="q-ml-md q-mb-lg"
              type="textarea"
              outlined
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Limitations</h6>
            <q-input
              v-model="creationStore.modelLimitations"
              placeholder="This model has the following limitations..."
              class="q-ml-md q-mb-lg"
              type="textarea"
              outlined
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
          </q-card-section>
        </q-card>
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
              This is the content that will be displayed on the model card page.
              You can use the "Populate card description" button to populate the
              markdown with the information you entered in the previous step.
            </p>
            <div
              class="text-left q-ml-md q-mb-md text-italic text-negative"
              v-if="
                creationStore.markdownContent.includes(
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
              :content="creationStore.markdownContent"
              :replace-content="replaceContent"
              @update:content="creationStore.markdownContent = $event"
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
          creationStore.performanceMarkdown.includes(
            'This is an example graph showcasing how the graph option works! Use the button on the toolbar to create new graphs. You can also edit preexisting graphs using the edit button!',
          ) == false
        "
        :error="
          creationStore.performanceMarkdown.includes(
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
              This is where you can add performance metrics for your model which
              will be displayed on the model card page. If you have supplied a
              linked experiment in the first step which includes logged metrics,
              you can use the "Retrieve plots from experiment" button to
              automatically generate plots for the logged metrics. If you have
              not supplied a linked experiment, you can use the "Add plot"
              button to manually add plots. You can also edit preexisting plots
              using the edit button.
            </p>
            <div
              class="text-left q-ml-md q-mb-md text-italic text-negative"
              v-if="
                creationStore.performanceMarkdown.includes(
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
              :content="creationStore.performanceMarkdown"
              @update:content="creationStore.performanceMarkdown = $event"
            >
              <template #toolbar>
                <q-btn
                  label="Retrieve plots from experiment"
                  rounded
                  no-caps
                  color="secondary"
                  @click="showPlotModal = true"
                  v-if="
                    creationStore.experimentPlatform != '' &&
                    creationStore.experimentID != ''
                  "
                />
              </template>
            </tiptap-editor>
          </div>
        </div>
      </q-step>

      <q-step
        :name="6"
        title="Inference Service"
        icon="code"
        :done="creationStore.step > 6"
        v-if="creationStore.modelTask != 'Reinforcement Learning'"
      >
        <div
          class="row justify-center"
          v-if="creationStore.modelTask != 'Reinforcement Learning'"
        >
          <div class="q-pa-md q-gutter-sm col-4 shadow-1">
            <h6 class="text-left q-mb-md">Setting Up an Inference Service</h6>
            <p class="text-left q-mb-md">
              To allow users to interact with your model, you will need to set
              up an inference service. This is a application (e.g Gradio,
              Streamlit) which provides a front-end inference interface for your
              model, which we will host and deploy for you.
            </p>
            <p class="text-left q-mb-md">
              If you have not already set up an inference service for your
              model, you can do so by clicking the button below. If you have
              already set up an inference service, you can skip this step.
            </p>
            <q-btn
              icon="check"
              color="secondary"
              label="I have set up an inference service application for my model"
              no-caps
              align="left"
              class="q-mb-sm float-left"
              style="width: 95.6%"
              unelevated
              @click="checkMetadata($refs.stepper)"
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
              href="https://dinohub.github.io/appstore-ai/user-guide/inference-services/building-inference-services.html"
              target="_blank"
            />
          </div>
        </div>
      </q-step>

      <q-step
        :name="7"
        title="Submission"
        icon="publish"
        :done="creationStore.step > 7"
        v-if="creationStore.modelTask != 'Reinforcement Learning'"
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-4 shadow-1">
            <h6 class="text-left q-mb-md q-mr-sm">Inference Engine</h6>
            <q-input
              outlined
              class="q-ml-md q-pb-xl"
              autogrow
              hint="Image URI"
              placeholder="e.g <registry>/<image>:<tag>"
              v-model="creationStore.imageUri"
              :loading="loadingExp"
              :disable="loadingExp"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => imageUriRegex.test(val) || 'Invalid Image URI',
              ]"
            ></q-input>
            <q-input
              outlined
              label="Number of GPUs"
              v-model="creationStore.numGpus"
              class="q-ml-md q-pb-xl"
              type="number"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => val >= 0 || 'Must be greater than or equal to 0',
                (val) => val <= 1 || 'Must be less than or equal to 1',
              ]"
              :loading="loadingExp"
              :disable="loadingExp"
              min="0"
              max="1"
            ></q-input>
            <!-- NOTE: temporarily disabled for now. See inferenceServiceStore to see reason why -->
            <!-- <q-input
              outlined
              v-model="creationStore.containerPort"
              class="q-ml-md q-pb-xl"
              label="Container Port (Optional)"
              hint="If not specified, container will listen on $PORT environment variable, which is automatically set to 8080 by default. "
              type="number"
              :loading="loadingExp"
              autogrow
            ></q-input> -->
            <env-var-editor
              mode="create"
              title-class="text-h6 text-left q-mt-md q-mb-lg"
              fieldset-class="q-ml-md"
              :loading="loadingExp"
              :disable="loadingExp"
            ></env-var-editor>
          </div>
        </div>
      </q-step>
      <q-step
        :name="7"
        title="Submission"
        icon="publish"
        :done="creationStore.step > 7"
        v-if="creationStore.modelTask == 'Reinforcement Learning'"
      >
        <div
          class="row justify-center"
          v-if="creationStore.modelTask == 'Reinforcement Learning'"
        >
          <div class="q-pa-md q-gutter-sm col-5 shadow-1">
            <h6 class="text-left q-mb-sm">
              Reinforcement Learning Example Video
            </h6>
            <p class="text-left">
              As a Reinforcement Learning algorithm showcase requires an
              environment, it may not be possible for a interactable demo to be
              displayed. In substitution, a video can be submitted in it's place
              that shows the agent's performance in the environment.
            </p>
            <div class="row justify-center text-center">
              <span class="text-negative text-italic q-pl-auto">
                <q-icon class="" name="priority_high" size="1.5rem" />
                The video should be under 10MB
                <q-icon class="" name="priority_high" size="1.5rem" />
              </span>
            </div>
            <div class="row justify-center text-center">
              <q-file
                v-model="creationStore.exampleVideo"
                label="Pick Video"
                filled
                counter
                max-file-size="10485760"
                accept="video/*"
                :counter-label="counterLabelFn"
                max-files="1"
                multiple
                :clearable="true"
                style="max-width: 100%; width: 60%"
                @update:model-value="createViewableVideo()"
              >
                <template v-slot:prepend>
                  <q-icon name="video_call" />
                </template>
              </q-file>
            </div>
          </div>
        </div>
      </q-step>
      <q-step :name="8" title="Confirm" icon="task">
        <div
          class="row justify-center"
          v-if="creationStore.modelTask != 'Reinforcement Learning'"
        >
          <div class="col-5">
            <gradio-frame
              debug-mode
              class="shadow-2"
              :v-show="creationStore.previewServiceUrl"
              :url="creationStore.previewServiceUrl ?? ''"
              :status="creationStore.previewServiceStatus ?? undefined"
            >
            </gradio-frame>
          </div>
          <div
            class="q-ml-xl col-3 shadow-2 rounded-borders q-my-auto"
            style="border-radius: 1; height: 60%"
          >
            <h6 class="text-left q-ml-md q-my-sm">Inference Engine</h6>
            <p class="text-left q-ml-md">
              The inference engine application will be displayed here. Please
              ensure it works as intended and can receive inputs and outputs as
              designed by you. If the app has not shown up for some time, you
              may want to click on the "View Status" button to see more details
              about what is happening.
            </p>
            <q-icon
              class="row q-mx-auto"
              name="warning"
              color="negative"
              size="1.75rem"
            />
            <p class="text-center text-bold q-px-lg text-negative">
              Ensure all information has been input correctly and the inference
              engine application is working as intended. Once confirmed all
              information will be published.
            </p>
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
          </div>
        </div>
        <div
          class="row justify-center q-mx-auto"
          v-if="creationStore.modelTask == 'Reinforcement Learning'"
          style="width: 37.5%"
        >
          <vue-plyr
            ><video controls playsinline>
              <source :src="videoExample" /></video
          ></vue-plyr>
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
              />
            </div>
            <div class="text-right col-6">
              <q-btn
                v-if="creationStore.step > 1"
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
                v-if="creationStore.step < 6"
                @click="$refs.stepper.next()"
                no-caps
                rounded
                color="primary"
                label="Continue"
                padding="sm xl"
                :disable="buttonDisable"
              />

              <q-btn
                v-if="creationStore.step == 7 && creationStore.imageUri != ''"
                @click="launchPreview($refs.stepper)"
                no-caps
                rounded
                color="primary"
                label="Submit Image"
                :disable="buttonDisable"
              />
              <q-btn
                v-if="
                  creationStore.step == 7 && creationStore.exampleVideo != null
                "
                @click="$refs.stepper.next()"
                no-caps
                rounded
                color="primary"
                label="Submit Video"
                :disable="buttonDisable"
              />

              <q-btn
                v-if="creationStore.step == 8"
                @click="finalSubmit($refs.stepper)"
                no-caps
                rounded
                color="primary"
                label="Confirm Model Card Creation"
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
            <span class="text-bold"
              >(Saving will override any previous creations)</span
            >
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              rounded
              outline
              no-caps
              label="Cancel"
              padding="sm xl"
              color="error"
              v-close-popup
            />
            <q-space />
            <q-btn
              rounded
              outline
              no-caps
              label="Quit"
              color="secondary"
              padding="sm xl"
              v-close-popup
              to="/"
              @click="flushCreator()"
            />
            <q-btn
              rounded
              no-caps
              label="Save & Quit"
              color="primary"
              padding="sm xl"
              outline
              v-if="local.getItem('createModel') != null"
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
            Populate markdown with your model card attributes?
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
            />
            <q-btn
              rounded
              no-caps
              padding="sm xl"
              label="Replace"
              color="primary"
              v-close-popup
              @click="populateEditor(creationStore)"
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
              @click="addExpPlots(creationStore)"
              :disable="buttonDisable"
            />
          </q-card-actions>
          <q-inner-loading :showing="buttonDisable">
            <q-spinner-gears size="50px" color="primary" />
          </q-inner-loading>
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
              outline
              rounded
              no-caps
              label="Delete"
              color="error"
              padding="sm xl"
              v-close-popup
              @click="flushCreator()"
            />
            <q-btn
              rounded
              no-caps
              padding="sm xl"
              label="Continue"
              color="primary"
              v-close-popup
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
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
    </dialog>
  </q-page>
</template>
<style>
.plyr--video {
  width: 100%;
}
</style>
<script setup lang="ts">
import { useExperimentStore } from 'src/stores/experiment-store';
import { useCreationStore } from 'src/stores/create-model-store';
import { useAuthStore } from 'src/stores/auth-store';
import {
  useInferenceServiceStore,
  imageUriRegex,
} from 'src/stores/inference-service-store';
import { useModelStore } from 'src/stores/model-store';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

import GradioFrame from 'src/components/content/GradioFrame.vue';
import TiptapEditor from 'src/components/editor/TiptapEditor.vue';
import EnvVarEditor from 'src/components/form/EnvVarEditor.vue';
import ServiceStatusDisplay from 'src/components/content/ServiceStatusDisplay.vue';

import { Notify, QStepper } from 'quasar';
import { useDatasetStore } from 'src/stores/dataset-store';

const router = useRouter();
// constants for stores
const experimentStore = useExperimentStore();
const datasetStore = useDatasetStore();
const creationStore = useCreationStore();
const modelStore = useModelStore();
const inferenceServiceStore = useInferenceServiceStore();

const videoExample = ref();

// for accessing localstorage
const local = localStorage;

// const for checking whether previous saves exist
const prevSave = ref(localStorage.getItem(`${creationStore.$id}`) != null);

// bool for loading state when retrieving experiments
const loadingExp = ref(false);
const replaceContent = ref(false); // indicator to replace content with model desc data
const replacePerformanceContent = ref(false); // indicator to replace content with model desc data

// variables for popup exits
const cancel = ref(false);
const popupContent = ref(false);
const showPlotModal = ref(false);
const buttonDisable = ref(false);
const showDetailedStatus = ref(false); // pop-up for service status

// function for triggering events that should happen when next step is triggered
const retrieveExperimentDetails = () => {
  loadingExp.value = true;
  buttonDisable.value = true;
  creationStore.loadMetadataFromExperiment().finally(() => {
    loadingExp.value = false; // don't lock user out when error
    buttonDisable.value = false;
  });
};

const retrieveDatasetDetails = () => {
  loadingExp.value = true;
  buttonDisable.value = true;
  creationStore.loadMetadataFromDataset().finally(() => {
    loadingExp.value = false; // don't lock user out when error
    buttonDisable.value = false;
  });
};

const createViewableVideo = () => {
  try {
    videoExample.value = URL.createObjectURL(creationStore.exampleVideo[0]);
  } catch {}
};

const counterLabelFn = ({ totalSize, filesNumber, maxFiles }: any) => {
  return `${filesNumber}/${maxFiles} File | ${totalSize}`;
};

const flushCreator = () => {
  // also remove any preview images
  const inferenceServiceStore = useInferenceServiceStore();
  if (inferenceServiceStore.previewServiceName) {
    inferenceServiceStore.deleteService(
      inferenceServiceStore.previewServiceName,
    );
  }
  creationStore.$reset();
  localStorage.removeItem(`${creationStore.$id}`);
};

const launchPreview = (stepper: QStepper) => {
  buttonDisable.value = true;
  loadingExp.value = true;
  creationStore
    .launchPreviewService(creationStore.modelName)
    .then(() => {
      stepper.next();
    })
    .catch((err) => {
      Notify.create({
        message: `Failed to launch preview! Error: ${err}`,
        color: 'negative',
      });
    })
    .finally(() => {
      buttonDisable.value = false;
      loadingExp.value = false;
    });
};

const checkMetadata = (stepper: QStepper) => {
  if (creationStore.metadataValid) {
    stepper.next();
  } else {
    Notify.create({
      message: 'Enter all values into required fields first before proceeding',
      icon: 'warning',
      color: 'negative',
    });
  }
};

const finalSubmit = (stepper: QStepper) => {
  if (creationStore.modelTask != 'Reinforcement Learning') {
    creationStore
      .createModel()
      .then((data) => {
        if (data) {
          flushCreator();
          router.push(`/model/${data.creatorUserId}/${data.modelId}`);
        }
      })
      .catch((err) => {
        Notify.create({
          message: err,
          icon: 'warning',
          color: 'negative',
        });
        console.error(err);
      });
  } else {
    if (creationStore.noServiceMetadataValid) {
      stepper.next();
      creationStore
        .createModelWithVideo()
        .then((data) => {
          if (data) {
            flushCreator();
            router.push(`/model/${data.creatorUserId}/${data.modelId}`);
          }
        })
        .catch((err) => {
          Notify.create({
            message: err,
            icon: 'warning',
            color: 'negative',
          });
          console.error(err);
        });
    } else {
      Notify.create({
        message:
          'Enter all values into required fields first before proceeding',
        icon: 'warning',
        color: 'negative',
      });
    }
  }
};

// function for populating editor with values from previous step
const populateEditor = (store: typeof creationStore) => {
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
};

const addExpPlots = (store: typeof creationStore) => {
  buttonDisable.value = true;
  let newPerformance = store.performanceMarkdown;
  if (store.experimentID) {
    experimentStore
      .getExperimentByID(store.experimentID, store.experimentPlatform, true)
      .then((data) => {
        store.plots = [...(data.plots ?? []), ...(data.scalars ?? [])];
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
        Notify.create({
          message: 'Successfully inserted plots from experiment',
          color: 'primary',
        });
      })
      .catch((err) => {
        Notify.create({
          message: 'Failed to insert plots',
          color: 'negative',
        });
        console.error(err);
      })
      .finally(() => {
        buttonDisable.value = false;
      });
  }
};

if (
  creationStore.step == 8 &&
  creationStore.modelTask == 'Reinforcement Learning'
) {
  creationStore.$patch({ step: 7 });
}
</script>
