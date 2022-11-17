<template>
  <q-page padding>
    <!-- content -->
    <model-card-edit-tabs />
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
          <div class="col-4 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Inference Service</h6>
            <!-- modelPath? -->
            <q-input
              outlined
              v-model="editInferenceServiceStore.imageUri"
              class="q-ml-md q-pb-xl"
              label="Container Image URI"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <!-- Below inputs do not do anything atm -->
            <q-input
              outlined
              class="q-ml-md q-pb-xl"
              label="Container Port (Optional)"
              hint="If not specified, container will listen on $PORT environment variable"
              type="number"
              autogrow
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="2"
        title="Test Inference Service"
        icon="mdi-server-network"
        done-editable
      >
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
                @click="$refs.stepper.next()"
                no-caps
                rounded
                color="primary"
                label="Continue"
                padding="sm xl"
                :disable="buttonDisable"
              />

              <q-btn
                v-if="
                  editInferenceServiceStore.step === 2 && false // TODO: check
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
              label="Cancel"
              padding="sm xl"
              color="error"
              v-close-popup
            />
            <q-space />
            <q-btn
              rounded
              outline
              label="Quit"
              color="secondary"
              v-close-popup
              to="/"
              @click="flushDraft()"
            />
            <q-btn
              rounded
              label="Save & Quit"
              color="primary"
              padding="sm xl"
              to="/"
              v-close-popup
              v-if="prevSave"
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
              outline
              rounded
              label="Delete"
              color="error"
              padding="sm xl"
              v-close-popup
              @click="flushDraft()"
            />
            <q-btn
              rounded
              padding="sm xl"
              label="Continue"
              color="primary"
              v-close-popup
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </dialog>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardEditTabs from 'src/components/layout/ModelCardEditTabs.vue';
import { useInferenceServiceStore } from 'src/stores/inference-service-store';
import { useEditInferenceServiceStore } from 'src/stores/edit-model-inference-service-store';
import { useModelStore } from 'src/stores/model-store';
import { useRoute } from 'vue-router';
import { ref, onMounted } from 'vue';

const route = useRoute();
const inferenceServiceStore = useInferenceServiceStore();
const editInferenceServiceStore = useEditInferenceServiceStore();
const modelStore = useModelStore();
const modelId = route.params.modelId as string;

const prevSave = ref(
  localStorage.getItem(editInferenceServiceStore.$id) !== null
);
const cancel = ref(false);
const popupContent = ref(false);
const buttonDisable = ref(false);

function flushDraft() {
  editInferenceServiceStore.$reset();
  localStorage.removeItem(`${editInferenceServiceStore.$id}`);
  editInferenceServiceStore.loadFromInferenceService(modelId); // we want to reset the store to the original model
}

onMounted(() => {
  if (!prevSave.value) {
    editInferenceServiceStore.loadFromInferenceService(modelId);
  }
});
</script>
