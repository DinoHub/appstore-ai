<template>
  <div ref="frame"></div>
</template>

<script setup lang="ts">
import { ref, Ref, watch, onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist';

/**
 * Plotly represents charts as a JSON object with two properties:
 * - data: an array of traces (e.g. lines, bars, etc.)
 * - layout: a JSON object that describes the layout of the chart
 */
export interface PlotlyChartProps {
  data: Record<string, any>[]; // 
  layout: Record<string, any>;
  responsive: boolean;
}

const props = withDefaults(defineProps<PlotlyChartProps>(), {
  responsive: true,
});

const frame: Ref<HTMLDivElement | undefined> = ref();

function renderPlot(
  chartRef: HTMLDivElement,
  { data, layout }: PlotlyChartProps,
) {
  chartRef.innerHTML = '';
  Plotly.purge(chartRef);
  Plotly.newPlot(chartRef, data, layout, {
    responsive: props.responsive,
  });
}

watch(props, (props) => {
  if (frame.value) {
    renderPlot(frame.value, props);
  }
});

onMounted(() => {
  if (frame.value) {
    renderPlot(frame.value, props);
  }
});
</script>
