<template>
  <q-chip
    :label="label"
    :icon="icon"
    :color="color ?? colorMapping[props.type]"
    :text-color="textColor ?? 'white'"
  ></q-chip>
</template>

<script setup lang="ts">
export interface Props {
  type: 'task' | 'framework' | 'tag';
  label?: string;
  icon?: string;
  color?: string;
  textColor?: string;
}

const colorMapping = {
  task: 'primary',
  framework: 'accent',
  tag: 'secondary',
};

const props = defineProps<Props>();
</script>
