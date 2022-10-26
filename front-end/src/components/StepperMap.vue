<template>
  <div class="q-pa-md col-9" :style="vert">
    <q-stepper
      v-model="step"
      ref="stepper"
      color="primary"
      animated
      done-color="secondary"
      class="shadow-0 justify-center text-center full-height"
      header-class="no-border q-px-xl"
    >
      <q-step
        :name="1"
        title="Model & Owner Information"
        icon="person"
        :done="step > 1"
      >
        <q-form @submit="onSubmit">
          <div class="row justify-center full-height">
            <div class="col-3 q-pr-md q-mr-xl shadow-2 rounded">
              <h6 class="text-left q-mt-md q-ml-md q-mb-lg">
                Model Information
              </h6>
              <q-input
                v-model="model_name"
                :dense="dense"
                class="q-ml-md q-pb-xl"
                hint="Model Name"
                :rules="[(val) => !!val || 'Field is required']"
              ></q-input>
              <q-select
                v-model="model"
                :dense="dense"
                class="q-ml-md q-pb-xl"
                :options="tasks"
                hint="Task"
                :rules="[(val) => !!val || 'Field is required']"
              />
            </div>
            <div class="col-3 q-mx-md shadow-2 rounded">
              <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Tags</h6>
              <q-select
                hint="Tags"
                v-model="tagAddUnique"
                use-input
                use-chips
                multiple
                autogrow
                hide-dropdown-icon
                input-debounce="0"
                new-value-mode="add-unique"
                class="q-ml-md q-pr-md q-pb-xl"
                :rules="[
                  (val) => val.length >= 1 || 'One or more tags required',
                ]"
              />
              <q-select
                hint="Frameworks"
                v-model="frameworkAddUnique"
                use-input
                use-chips
                multiple
                autogrow
                hide-dropdown-icon
                input-debounce="0"
                new-value-mode="add-unique"
                class="q-ml-md q-pr-md q-pb-xl"
                :rules="[
                  (val) => val.length >= 1 || 'One or more frameworks required',
                ]"
              ></q-select>
            </div>
            <div class="col-3 q-pl-md q-ml-xl shadow-2 rounded">
              <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
              <q-input
                v-model="owner"
                :dense="dense"
                class="q-mr-md q-pb-xl"
                hint="Model Owner (Optional)"
              ></q-input>
              <q-input
                v-model="poc"
                :dense="dense"
                class="q-mr-md q-pb-xl"
                hint="Point of Contact (Optional)"
              ></q-input>
            </div>
          </div>
        </q-form>
      </q-step>

      <q-step :name="2" title="Links" icon="link" :done="step > 2"> </q-step>
      <q-step
        :name="3"
        title="Card Description"
        icon="description"
        :done="step > 3"
      >
      </q-step>

      <q-step
        :name="4"
        title="Performance Metrics"
        icon="leaderboard"
        :done="step > 4"
      >
      </q-step>

      <q-step :name="5" title="Inference Engine" icon="code"> </q-step>

      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row">
            <div class="text-left col-2">
              <q-btn color="red" to="/" label="Cancel" class="q-mr-md" />
            </div>
            <div class="text-right col-10">
              <q-btn
                v-if="step > 1"
                color="primary"
                @click="$refs.stepper.previous()"
                label="Back"
                class="q-mr-md"
              />
              <q-btn
                v-if="step != 5"
                @click="
                  $refs.stepper.next();
                  simulateSubmit();
                "
                color="primary"
                label="Continue"
              />
            </div>
          </div>
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const step = ref(1);
    const tagAddUnique = ref([]);
    const frameworkAddUnique = ref([]);
    const model_name = ref('');
    const owner = ref('');
    const poc = ref('');
    function simulateSubmit() {
      console.log(tagAddUnique.value);
      console.log(frameworkAddUnique.value);
    }
    return {
      step,
      simulateSubmit,
      tagAddUnique,
      frameworkAddUnique,
      model: ref(null),
      model_name,
      owner,
      poc,
      tasks: [
        'Computer Vision',
        'Natural Language Processing',
        'Audio Processing',
        'Multimodal',
        'Reinforcement Learning',
        'Tabular',
      ],
    };
  },
};
</script>
