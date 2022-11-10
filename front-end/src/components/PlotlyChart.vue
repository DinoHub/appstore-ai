<template>
  <div ref="frame"></div>
</template>

<script setup lang="ts">
import { ref, Ref, watch, onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist';

export interface Props {
  data: Record<string, any>[];
  layout: Record<string, any>;
  responsive: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  responsive: true,
});

const frame: Ref<HTMLDivElement | undefined> = ref();

function renderPlot(chartRef: HTMLDivElement, props: Props) {
  const { data, layout } = props;
  Plotly.newPlot(chartRef, data, layout, {
    responsive: props.responsive,
  });
}

watch(props, (props) => {
  if (!frame.value) {
    return;
  }
  renderPlot(frame.value, props);
});

onMounted(() => {
  if (!frame.value) {
  }
  renderPlot(frame.value, props);
});
</script>
