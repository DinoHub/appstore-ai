<template>
  <!-- Form to set environment variables for an inference service -->
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
      :disable="disable"
    ></q-btn>
    <div
      class="row"
      :class="fieldsetClass"
      v-for="idx in Array(store.env.length).keys()"
      :key="idx"
    >
      <!-- Display error if some variables have same name -->
      <q-input
        outlined
        label="Key"
        v-model="store.env[idx].key"
        class="col q-mr-sm"
        reactive-rules
        :rules="[(val) => !checkDuplicateEnvVar(val)]"
        :disable="disable"
        :loading="loading"
      ></q-input>
      <q-input
        outlined
        label="Value"
        v-model="store.env[idx].value"
        class="col q-mr-sm"
        :disable="disable"
        :loading="loading"
      ></q-input>
      <q-btn
        rounded
        flat
        dense
        icon="delete"
        color="error"
        class="col-1 q-mb-md"
        @click="deleteField(idx)"
        :disable="disable"
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
  loading: boolean;
  disable: boolean;
}

const props = withDefaults(defineProps<EnvVarEditorProps>(), {
  titleClass: '',
  containerClass: '',
  fieldsetClass: '',
});

// Update different store depending on mode
// NOTE: this is somewhat hacky and should be refactored
// e.g passing in store as prop
const store =
  props.mode === 'create' ? useCreationStore() : useEditInferenceServiceStore();

const addField = () =>
  store.env.push({
    key: '',
    value: '',
  });
const deleteField = (idx: number) => store.env.splice(idx, 1);
const checkDuplicateEnvVar = (val: string) =>
  store.env.filter(({ key }) => key.trim() === val.trim()).length > 1;
</script>
