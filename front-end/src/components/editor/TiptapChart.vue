<template>
  <node-view-wrapper>
    <q-card>
      <q-btn
        v-if="props.editor.isEditable"
        label="Edit Chart"
        color="primary"
        @click="chartEditor = true"
      >
      </q-btn>
      <q-dialog persistent full-width full-height v-model="chartEditor">
        <plotly-editor
          @update-plot="update"
          update
          :data="JSON.parse(props.node.attrs.data)"
          :layout="JSON.parse(props.node.attrs.layout)"
        ></plotly-editor>
      </q-dialog>
      <q-card-section>
        <plotly-chart
          :data="JSON.parse(props.node.attrs.data)"
          :layout="JSON.parse(props.node.attrs.layout)"
        ></plotly-chart>
      </q-card-section>
    </q-card>
  </node-view-wrapper>
</template>

<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3';
import { ref } from 'vue';
import PlotlyChart from '../content/PlotlyChart.vue';
import PlotlyEditor from './PlotlyEditor.vue';

const props = defineProps(nodeViewProps);

const chartEditor = ref(false);

function update(data: Record<string, any>[], layout: Record<string, any>) {
  props.updateAttributes({
    layout: JSON.stringify(layout),
    data: JSON.stringify(data),
  });
}
</script>
