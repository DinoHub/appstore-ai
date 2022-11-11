<template>
  <q-card>
    <q-card-section>
      <div class="text-h5">Chart Editor</div>
      <!-- Editor -->
      <q-tabs
        v-model="tab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="data" label="Data"> </q-tab>
        <q-tab name="preview" label="Preview Graph"> </q-tab>
      </q-tabs>
      <q-separator></q-separator>
      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="data">
          <div class="text-h6">Data</div>
          <JSONEditorVue v-model="data"></JSONEditorVue>
          <div class="text-h6">Layout</div>
          <JSONEditorVue v-model="layout"></JSONEditorVue>
        </q-tab-panel>
        <q-tab-panel name="preview">
          <plotly-chart :data="data" :layout="layout"></plotly-chart>
        </q-tab-panel>
      </q-tab-panels>
    </q-card-section>
    <q-card-actions>
      <q-btn color="primary" v-if="props.update" v-close-popup @click="update"
        >Update Chart</q-btn
      >
      <q-btn color="primary" v-else v-close-popup @click="insert"
        >Create Chart</q-btn
      >
      <q-btn color="red" v-close-popup>Close without saving</q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import PlotlyChart from '../content/PlotlyChart.vue';
import JSONEditorVue from 'json-editor-vue';
import { Ref, ref, watch } from 'vue';

export interface Props {
  data?: Record<string, any>[];
  layout?: Record<string, any>;
  update?: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits(['updatePlot', 'newPlot']);

const tab = ref('data');
const data: Ref<Record<string, any>[]> = ref(
  props.data ?? [
    {
      x: [],
      y: [],
      type: 'scatter',
    },
  ]
);
const layout: Ref<Record<string, any>> = ref(
  props.layout ?? {
    title: 'New Chart',
    xaxis: {
      title: 'X Axis Label',
    },
    yaxis: {
      title: 'Y Axis Label',
    },
  }
);

function update() {
  console.log('Updating Plot');
  emit('updatePlot', data.value, layout.value);
}

function insert() {
  console.log('Creating Plot');
  emit('newPlot', data.value, layout.value);
}

watch(data, (newData) => {
  // Sometimes new data is a string, so we need to parse it
  // Check if string
  if (typeof newData === 'string') {
    // Parse string
    data.value = JSON.parse(newData);
  }
});

watch(layout, (newLayout) => {
  // Sometimes new data is a string, so we need to parse it
  // Check if string
  if (typeof newLayout === 'string') {
    // Parse string
    layout.value = JSON.parse(newLayout);
  }
});
</script>
