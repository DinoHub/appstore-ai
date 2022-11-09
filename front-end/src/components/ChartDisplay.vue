<template>
  <node-view-wrapper>
    <h5>Hello Chart</h5>
    <q-btn label="Edit Chart" @click="update"> </q-btn>
    <div :id="chartId"></div>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import {
  NodeViewContent,
  NodeViewProps,
  nodeViewProps,
  NodeViewWrapper,
} from '@tiptap/vue-3';
import * as Plotly from 'plotly.js-dist';
import { onMounted, watch } from 'vue';

const props = defineProps(nodeViewProps);

const chartId = `chart-${crypto.randomUUID()}`;
function renderPlot(el: HTMLElement, props: NodeViewProps) {
  const data = JSON.parse(props.node.attrs.data);
  const layout = JSON.parse(props.node.attrs.layout);
  Plotly.newPlot(el, data, layout, {
    responsive: true,
  });
}

const update = () => {
  props.updateAttributes({
    layout: JSON.stringify({
      title: 'update',
    }),
  });
};

watch(props, (props) => {
  const chartRef = document.getElementById(chartId);
  if (chartRef) {
    renderPlot(chartRef, props);
  }
});

onMounted(() => {
  const chartRef = document.getElementById(chartId);
  renderPlot(chartRef, props);
});

// })
</script>

<style scoped></style>
