<template>
  <q-page padding>
    <!-- content -->
    <admin-model-card-edit-tabs :task="''" />
    <q-stepper
      v-model="editInferenceServiceStore.step"
      animated
      ref="stepper"
      done-color="primary"
      error-color="error"
      active-color="secondary"
    >
      <q-step
        :name="1"
        title="Inference Service"
        icon="mdi-server"
        done-editable
        :done="editInferenceServiceStore.imageUri != ''"
        :error="editInferenceServiceStore.imageUri == ''"
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-6 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Inference Service</h6>
            <!-- modelPath? -->
            <q-input
              outlined
              v-model="editInferenceServiceStore.imageUri"
              class="q-ml-md q-pb-xl"
              label="Container Image URI"
              placeholder="e.g <registry>/<image>:<tag>"
              autogrow
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => imageUriRegex.test(val) || 'Invalid Image URI',
              ]"
              :loading="loading"
              :disable="loading"
            ></q-input>
            <q-input
              outlined
              label="Number of GPUs"
              v-model="editInferenceServiceStore.numGpus"
              class="q-ml-md q-pb-xl"
              type="number"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => val >= 0 || 'Must be greater than or equal to 0',
                (val) => val <= 1 || 'Must be less than or equal to 1',
              ]"
              :loading="loading"
              :disable="loading"
              min="0"
              max="1"
            ></q-input>
            <!-- NOTE: Disable ability to set port number temporarily as Emissary backend is hard coded to port 8080 -->
            <!-- <q-input
              outlined
              v-model="editInferenceServiceStore.containerPort"
              class="q-ml-md q-pb-xl"
              label="Container Port (Optional)"
              hint="If not specified, container will listen on $PORT environment variable, which is set to 8080 by default."
              type="number"
              autogrow
            ></q-input> -->
            <!-- Define Environment Variables -->
            <env-var-editor
              mode="edit"
              title-class="text-h6 text-left q-mt-md q-ml-md q-mb-lg"
              fieldset-class="q-ml-md"
              :loading="loading"
              :disable="loading"
            >
            </env-var-editor>
          </div>
        </div>
      </q-step>
      <q-step
        :name="2"
        title="Test Inference Service"
        icon="mdi-server-network"
        done-editable
      >
        <gradio-frame
          debug-mode
          :v-show="editInferenceServiceStore.previewServiceUrl"
          :url="editInferenceServiceStore.previewServiceUrl ?? ''"
          :status="editInferenceServiceStore.previewServiceStatus ?? undefined"
          class="col"
        ></gradio-frame>
        <!-- Redundant to show this once gradio frame is ready as it alr contains status-->
        <q-card v-if="!editInferenceServiceStore.previewServiceUrl">
          <q-card-section>
            <p>Preparing service...</p>
            <p>
              If the app has not shown up for some time, you may want to click
              on the "View Status" button to see more details about what is
              happening.
            </p>
          </q-card-section>
          <q-card-actions>
            <q-btn
              class="q-my-md"
              rounded
              no-caps
              padding="sm xl"
              label="View Status (Debug)"
              @click="showDetailedStatus = true"
            />
          </q-card-actions>
        </q-card>
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
                v-if="editInferenceServiceStore.step > 1"
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
                v-if="editInferenceServiceStore.step < 2"
                @click="launchPreview($refs.stepper)"
                no-caps
                rounded
                color="primary"
                label="Continue"
                padding="sm xl"
                :disable="
                  editInferenceServiceStore.imageUri === '' || buttonDisable
                "
              />
              <q-btn
                v-if="
                  editInferenceServiceStore.step === 2 &&
                  editInferenceServiceStore.imageUri
                "
                @click="updateService()"
                no-caps
                rounded
                color="primary"
                padding="sm xl"
                label="Update Service"
                :disable="buttonDisable"
              />
            </div>
          </div>
        </q-stepper-navigation>
      </template>
      <q-inner-loading :showing="loading"
        ><q-spinner-gears size="50px" color="primary"></q-spinner-gears
      ></q-inner-loading>
    </q-stepper>
    <dialog>
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
      <q-dialog v-model="cancel" persistent>
        <q-card>
          <q-card-section>
            <div class="text-h6">Quit</div>
          </q-card-section>
          <q-card-section class="q-pt-none">
            Are you sure you want to exit? <br />
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              no-caps
              rounded
              outline
              label="Cancel"
              padding="sm xl"
              color="error"
              @click="onCancel"
              v-close-popup
            />
            <q-space />
            <q-btn
              no-caps
              rounded
              outline
              label="Quit"
              color="secondary"
              v-close-popup
              to="/admin/models"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </dialog>
  </q-page>
</template>

<script setup lang="ts">
import AdminModelCardEditTabs from 'src/components/layout/AdminModelCardEditTabs.vue';
import GradioFrame from 'src/components/content/GradioFrame.vue';
import EnvVarEditor from 'src/components/form/EnvVarEditor.vue';
import ServiceStatusDisplay from 'src/components/content/ServiceStatusDisplay.vue';
import {
  useInferenceServiceStore,
  InferenceServiceStatus,
  imageUriRegex,
} from 'src/stores/inference-service-store';
import { useEditInferenceServiceStore } from 'src/stores/edit-model-inference-service-store';
import { useRoute, useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
import { Notify, QStepper } from 'quasar';

const route = useRoute();
const router = useRouter();
const inferenceServiceStore = useInferenceServiceStore();
const editInferenceServiceStore = useEditInferenceServiceStore();
const modelId = route.params.modelId as string;
const userId = route.params.userId as string;

const buttonDisable = ref(false);
const loading = ref(false);
const cancel = ref(false);
const showDetailedStatus = ref(false);
const inferenceStatus: Ref<InferenceServiceStatus | undefined> = ref();

const launchPreview = (stepper: QStepper) => {
  buttonDisable.value = true;
  loading.value = true;

  editInferenceServiceStore
    .launchPreviewService(modelId)
    .then(() => {
      stepper.next();
    })
    .catch((err) => {
      console.error(err);
    })
    .finally(() => {
      loading.value = false;
      buttonDisable.value = false;
    });
};

const updateService = () => {
  const previewServiceName = editInferenceServiceStore.previewServiceName;
  editInferenceServiceStore
    .updateInferenceService(userId, modelId)
    .then(() => {
      Notify.create({
        message: 'Inference Service updated',
        icon: 'check',
        color: 'primary',
      });
      router.push(`/admin/models`);
    })
    .catch((err) => {
      Notify.create({
        message: `Failed to update Inference Service. Error: ${err}`,
        icon: 'warning',
        color: 'negative',
      });
    });
  if (previewServiceName) {
    // Remove preview service
    inferenceServiceStore.deleteService(previewServiceName);
  }
};

const onCancel = () => {
  const previewServiceName = editInferenceServiceStore.previewServiceName;
  if (previewServiceName) {
    // Remove preview service
    inferenceServiceStore.deleteService(previewServiceName);
  }
};

onMounted(() => {
  editInferenceServiceStore.loadFromInferenceService(modelId, userId);
});
</script>
