<template>
  <node-view-wrapper>
    <q-card>
      <q-card-actions align="right">
        <q-btn
          v-if="props.editor.isEditable"
          round
          flat
          icon="delete"
          color="error"
          @click="deleteChart = true"
        >
          <q-dialog v-model="deleteChart">
            <q-card>
              <q-card-section class="row items-center">
                <q-icon name="warning" color="warning" />
                <span class="q-ml-sm"
                  >Are you sure you want to delete this chart?</span
                >
              </q-card-section>
              <q-card-actions align="right">
                <q-btn
                  no-caps
                  rounded
                  outline
                  flat
                  label="Cancel"
                  color="primary"
                  v-close-popup
                />
                <q-btn
                  no-caps
                  rounded
                  label="Delete"
                  color="error"
                  v-close-popup
                  @click="props.deleteNode()"
                />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </q-btn>
        <q-btn
          v-if="props.editor.isEditable"
          round
          flat
          icon="edit"
          color="primary"
          @click="chartEditor = true"
        >
        </q-btn>
      </q-card-actions>
      <q-dialog persistent full-width full-height v-model="chartEditor">
        <!-- Listen to update plot event, and call update callback -->
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
const deleteChart = ref(false);

// When the chart is updated, update the attributes
const update = (data: Record<string, any>[], layout: Record<string, any>) => {
  props.updateAttributes({
    layout: JSON.stringify(layout),
    data: JSON.stringify(data),
  });
};
</script>
