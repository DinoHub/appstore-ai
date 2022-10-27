<template>
  <article v-html="convertedMarkdown"></article>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it';
import { defineProps, Ref, ref, watch } from 'vue';
interface Props {
  markdown: string;
}
const props = defineProps<Props>();
const md = new MarkdownIt();

// Render Markdown
const convertedMarkdown: Ref<string> = ref('');

watch(props, (props) => {
  // When parent component gets the model card info, then update the markdown to show
  convertedMarkdown.value = md.render(props.markdown);
});
</script>
