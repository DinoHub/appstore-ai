<style>
h1 {
  font-size: 3rem;
}

h2 {
  font-size: 2.5rem;
}

h3 {
  font-size: 2rem;
}

h4 {
  font-size: 1.5rem;
}

h5 {
  font-size: 1.25rem;
}

h6 {
  font-size: 1rem;
}
</style>

<template>
  <article v-html="convertedMarkdown"></article>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import { defineProps, Ref, ref, watch } from 'vue';
interface Props {
  markdown: string;
}
const props = defineProps<Props>();
const md = new MarkdownIt(
  {
    html: true,
    highlight: (str, lang) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(str, { language: lang }).value;
        } catch (__) {}
      }
      return ''; // use external default escaping
    },
    linkify: true
  }
);

// Render Markdown
const convertedMarkdown: Ref<string> = ref('');

watch(props, (props) => {
  // When parent component gets the model card info, then update the markdown to show
  convertedMarkdown.value = md.render(props.markdown);
});
</script>
