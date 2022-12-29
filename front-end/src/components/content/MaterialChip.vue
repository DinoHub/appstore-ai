<template>
  <q-chip
    :label="label"
    :icon="icon"
    :color="color ?? colorMapping[props.type]"
    :text-color="textColor ?? 'surface'"
  ></q-chip>
</template>

<script setup lang="ts">
export interface MaterialChipProps {
  type: 'task' | 'framework' | 'tag';
  label?: string;
  icon?: string;
  color?: string;
  textColor?: string;
}

const colorMapping = {
  task: 'primary',
  framework: 'tertiary',
  tag: 'secondary',
};

const props = withDefaults(defineProps<MaterialChipProps>(), {
  type: 'tag',
});
</script>
