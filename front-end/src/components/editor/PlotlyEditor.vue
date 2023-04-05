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
      <q-tab-panels v-model="tab" animated keep-alive>
        <q-tab-panel name="data" class="json-editor">
          <div class="text-h6">Data</div>
          <JSONEditorVue
            :onRenderValue="onRenderValueData"
            v-model="data"
            mode="text"
          ></JSONEditorVue>
          <div class="text-h6">Layout</div>
          <JSONEditorVue v-model="layout" mode="text"></JSONEditorVue>
        </q-tab-panel>
        <q-tab-panel name="preview">
          <!-- Preview chart -->
          <plotly-chart
            v-if="tab == Tabs.preview"
            :data="parsedData"
            :layout="parsedLayout"
          ></plotly-chart>
        </q-tab-panel>
      </q-tab-panels>
    </q-card-section>
    <q-card-actions>
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        color="primary"
        v-if="props.update"
        v-close-popup
        @click="updateChart"
        >Update Chart</q-btn
      >
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        color="primary"
        v-else
        v-close-popup
        @click="insertChart"
        >Create Chart</q-btn
      >
      <q-btn rounded no-caps padding="sm xl" color="red" v-close-popup
        >Close without saving</q-btn
      >
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import PlotlyChart from '../content/PlotlyChart.vue';
import JSONEditorVue from 'json-editor-vue';
import {
  renderJSONSchemaEnum, // TODO: use this with Plotly json schema to render dropdowns
  renderValue,
  RenderValueProps,
} from 'vanilla-jsoneditor';
import { Ref, ref } from 'vue';
import { computedEager } from '@vueuse/core';

export interface PlotlyEditorProps {
  data?: Record<string, any>[];
  layout?: Record<string, any>;
  update?: boolean;
}

enum Tabs {
  data = 'data',
  preview = 'preview',
}

const props = withDefaults(defineProps<PlotlyEditorProps>(), {
  update: false,
});

const emit = defineEmits(['updatePlot', 'newPlot']);

const tab: Ref<Tabs> = ref(Tabs.data);

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

const updateChart = () => { 
  // Sometimes new data is a string, so we need to parse it
  if (typeof data.value === 'string') {
    data.value = JSON.parse(data.value);
  }
  if (typeof layout.value === 'string') {
    layout.value = JSON.parse(layout.value);
  }
  emit('updatePlot', data.value, layout.value);
}
const insertChart = () => { 
  if (typeof data.value === 'string') {
    data.value = JSON.parse(data.value);
  }
  if (typeof layout.value === 'string') {
    layout.value = JSON.parse(layout.value);
  }
  emit('newPlot', data.value, layout.value);
}
// TODO: Use Plotly Schema at https://api.plot.ly/v2/plot-schema?format=json&sha1=%27%27
const onRenderValueData = (props: RenderValueProps) => renderValue(props);

// Need computed eager as lazy evaluation
// will cause an infinite loop even when
// data does not change
// causing app to crash due to the chart
// always updating
const parsedData = computedEager(() => {
  // Sometimes new data is a string, so we need to parse it
  // Check if string
  if (typeof data.value === 'string') {
    // Parse string
    return JSON.parse(data.value);
  }
  return data.value;
});

const parsedLayout = computedEager(() => {
  // Sometimes new data is a string, so we need to parse it
  // Check if string
  if (typeof layout.value === 'string') {
    // Parse string
    return JSON.parse(layout.value);
  }
  return layout.value;
});

</script>

<style>
.json-editor {
  --jse-font-family: var(--md-sys-typescale-body-small-font-family-name);
  --jse-theme-color: var(--md-sys-color-primary);
  --jse-theme-color-highlight: var(--md-sys-color-secondary);
  --jse-error-color: var(--md-sys-color-error);
  --jse-warning-color: #f2c037;
}
</style>
