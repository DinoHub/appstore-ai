<template>
  <q-page padding>
    <!-- content -->
    <admin-model-card-edit-tabs :task="'Reinforcement Learning'" />
    <q-stepper
      v-model="step"
      animated
      ref="stepper"
      done-color="primary"
      error-color="error"
    >
      <q-step :name="1" title="Video Submission" icon="publish">
        <div class="row justify-center">
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
                v-model="selectedVideo"
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
      <q-step
        :name="2"
        class="q-mx-auto"
        title="Confirm"
        icon="task"
        style="width: 37.5%"
      >
        <div class="justify-center">
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
                v-if="step == 2"
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
                v-if="step == 1 && selectedVideo"
                no-caps
                rounded
                @click="$refs.stepper.next()"
                color="primary"
                label="Continue"
                padding="sm xl"
              />
              <q-btn
                v-if="step == 2"
                no-caps
                rounded
                color="primary"
                padding="sm xl"
                label="Update Video"
                @click="replaceVideo()"
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
              no-caps
              rounded
              outline
              label="Cancel"
              padding="sm xl"
              color="error"
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
<style>
.plyr--video {
  width: 100%;
}
</style>
<script setup lang="ts">
import AdminModelCardEditTabs from 'src/components/layout/AdminModelCardEditTabs.vue';
import { useModelStore } from 'src/stores/model-store';
import { useAuthStore } from 'src/stores/auth-store';
import { useUploadStore } from 'src/stores/upload-store';
import { useRoute, useRouter } from 'vue-router';
import { ref } from 'vue';
import { QStepper } from 'quasar';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const modelStore = useModelStore();
const uploadStore = useUploadStore();

const cancel = ref(false);
const buttonDisable = ref(false);
const loading = ref(false);
const step = ref(1);
const videoExample = ref();
const selectedVideo = ref();

const modelId = route.params.modelId as string;
const userId = route.params.userId as string;

const replaceVideo = () => {
  // backend will handle the case where video
  // did not exist beforehand
  uploadStore.replaceVideo(selectedVideo.value, userId, modelId).then(() => {
    router.push(`/admin/models`);
  });
};

const counterLabelFn = ({ totalSize, filesNumber, maxFiles }: any) => {
  return `${filesNumber}/${maxFiles} File | ${totalSize}`;
};

const createViewableVideo = () => {
  try {
    videoExample.value = URL.createObjectURL(selectedVideo.value[0]);
  } catch {}
};
</script>
