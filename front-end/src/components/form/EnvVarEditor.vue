<template>
  <form :class="containerClass">
    <span :class="titleClass">
      <slot name="title">Set Environment Variables</slot>
    </span>
    <q-btn
      rounded
      outline
      no-caps
      color="primary"
      label="Add Environment Variable"
      icon="add"
      class="row q-ml-md q-mb-md"
      padding="sm xl"
      @click="addField"
    ></q-btn>
    <div
      class="row"
      :class="fieldsetClass"
      v-for="idx in Array(store.env.length).keys()"
      :key="idx"
    >
      <q-input
        outlined
        label="Key"
        v-model="store.env[idx].key"
        class="col q-mr-sm"
        reactive-rules
        :rules="[(val) => !checkDuplicateEnvVar(val)]"
      ></q-input>
      <q-input
        outlined
        label="Value"
        v-model="store.env[idx].value"
        class="col q-mr-sm"
      ></q-input>
      <q-btn
        rounded
        flat
        dense
        icon="delete"
        color="error"
        class="col-1 q-mb-md"
        @click="deleteField(idx)"
      ></q-btn>
    </div>
  </form>
</template>

<script setup lang="ts">
import { useCreationStore } from 'src/stores/create-model-store';
import { useEditInferenceServiceStore } from 'src/stores/edit-model-inference-service-store';

export interface EnvVarEditorProps {
  mode: 'create' | 'edit';
  containerClass: string;
  fieldsetClass: string;
  titleClass: string;
}

const props = withDefaults(defineProps<EnvVarEditorProps>(), {
  titleClass: '',
  containerClass: '',
  fieldsetClass: '',
});

const store =
  props.mode === 'create' ? useCreationStore() : useEditInferenceServiceStore();

const addField = () =>
  store.env.push({
    key: '',
    value: '',
  });
const deleteField = (idx: number) => store.env.splice(idx, 1);
const checkDuplicateEnvVar = (val: string) =>
  store.env.filter(({ key }) => key === val).length > 1;
</script>