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
        <gradio-frame :v-show="previewUrl" :url="previewUrl"></gradio-frame>
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
                @click="launchPreview($refs.stepper)"
                no-caps
                rounded
                color="primary"
                label="Continue"
                padding="sm xl"
                :disable="
                  editInferenceServiceStore.imageUri === '' && buttonDisable
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
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </dialog>
  </q-page>
</template>

<script setup lang="ts">
import ModelCardEditTabs from 'src/components/layout/ModelCardEditTabs.vue';
import GradioFrame from 'src/components/content/GradioFrame.vue';
import { useInferenceServiceStore } from 'src/stores/inference-service-store';
import { useEditInferenceServiceStore } from 'src/stores/edit-model-inference-service-store';
import { useAuthStore } from 'src/stores/auth-store';
import { useModelStore } from 'src/stores/model-store';
import { useRoute, useRouter } from 'vue-router';
import { ref, Ref, onMounted } from 'vue';
import { Notify, QStepper } from 'quasar';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const inferenceServiceStore = useInferenceServiceStore();
const editInferenceServiceStore = useEditInferenceServiceStore();
const modelStore = useModelStore();
const modelId = route.params.modelId as string;
const previewUrl: Ref<string | null> = ref(null);

const cancel = ref(false);
const popupContent = ref(false);
const buttonDisable = ref(false);
const loading = ref(false);

const launchPreview = (stepper: QStepper) => {
  buttonDisable.value = true;
  loading.value = true;
  inferenceServiceStore
    .createService(
      modelId,
      editInferenceServiceStore.imageUri,
      editInferenceServiceStore.containerPort,
    )
    .then((data) => {
      // Check for status
      inferenceServiceStore
        .getServiceReady(data.serviceName, 5, 10)
        .then((ready) => {
          if (ready) {
            editInferenceServiceStore.previewServiceName = data.serviceName;
            previewUrl.value = data.inferenceUrl;
            stepper.next();
          } else {
            Notify.create({
              message: 'Service did not sucessfully start',
              color: 'error',
            });
          }
        })
        .catch((err) => {
          Notify.create({
            message: 'Failed to create service',
            color: 'error',
          });
        });
    })
    .catch(() => {
      Notify.create({
        message: 'Failed to launch preview of inference engine',
        icon: 'check',
        color: 'error',
      });
    })
    .finally(() => {
      loading.value = false;
      buttonDisable.value = false;
    });
};

const updateService = () => {
  const previewServiceName = editInferenceServiceStore.previewServiceName;
  inferenceServiceStore
    .updateService(
      editInferenceServiceStore.serviceName,
      editInferenceServiceStore.imageUri,
      editInferenceServiceStore.containerPort,
    )
    .then((data) => {
      console.log('Inference service updated');
      Notify.create({
        message: 'Inference Service updated',
        icon: 'check',
        color: 'primary',
      });
      router.push(`/model/${authStore.user?.userId}/${modelId}`);
    });
  if (previewServiceName) {
    // Remove preview service
    inferenceServiceStore.deleteService(previewServiceName);
  }
};

onMounted(() => {
  editInferenceServiceStore.loadFromInferenceService(modelId);
});
</script>
