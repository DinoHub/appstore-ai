<template>
  <div class="q-pa-md" :style="vert">
    <q-stepper
      v-model="step"
      ref="stepper"
      color="primary"
      animated
      done-color="secondary"
      class="shadow-0 "
      header-class="no-border"
      
    >
      <q-step
        :name="1"
        title="Model & Owner Information" 
        icon="person"
        :done="step > 1"
      >
      </q-step>

      <q-step
        :name="2"
        title="Card Description"
        icon="description"
        :done="step > 2"
      >
      </q-step>

      <q-step
        :name="3"
        title="Performance Metrics"
        icon="leaderboard"
        :done="step > 3"
      >
      </q-step>

      <q-step :name="4" title="Inference Engine" icon="code"> </q-step>

      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row">
            <div class="text-left col-2">
              <q-btn
                color="red"
                @click="$refs.stepper.previous()"
                label="Cancel"
                class="q-mr-md"
              />
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
                v-if="step != 4"
                @click="$refs.stepper.next()"
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
    return {
      step: ref(1),
    };
  },
};
</script>
