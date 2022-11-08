<style>
h1 {
  font-size: 2.25rem;
}

h2 {
  font-size: 2rem;
}

h3 {
  font-size: 1.75rem;
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
  <article ref="mdRef"></article>
</template>

<script setup lang="ts">
import { Chart } from './models';
import * as Plotly from 'plotly.js-dist';
import MarkdownIt from 'markdown-it';
import customContainer from 'markdown-it-container';
import hljs from 'highlight.js';
import { defineProps, reactive, Ref, ref, watch } from 'vue';
import DOMPurify from 'dompurify';
interface Props {
  markdown: string;
}

// TinyMCE uses <br> for line breaks which hljs cannot render
hljs.addPlugin({
  'before:highlightElement': ({ el }) => {
    el.textContent = el.innerText;
  },
});

const props = defineProps<Props>();

const chartData: Chart[] = reactive([]);
const md = new MarkdownIt({
  html: true,
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value;
      } catch (__) {}
    }
    return ''; // use external default escaping
  },
  linkify: true,
  breaks: true,
}).use(customContainer, 'chart', {
  render: (tokens: { info: string; nesting: number }[], idx: number) => {
    const m = tokens[idx].info.trim().match(/^chart\s+(.*)$/);
    // opening tag, content
    if (m && tokens[idx].nesting === 1) {
      try {
        // Add chart
        let chartId = `chart-${crypto.randomUUID()}`;
        const data: Chart = JSON.parse(m[1].trim());
        chartData.push({
          id: chartId,
          data: data.data, // https://portswigger.net/web-security/dom-based/client-side-json-injection
          layout: data.layout,
        });
        return `<div class="q-card"><div id="${chartId}" class="q-card__section q-card"></div>`; // plotly will use chartid and dynamically render
      } catch (error) {
        alert(error);
        return '<pre>Error!</pre>';
      }
    } else {
      return '</div>';
    }
  },
  marker: '`',
});

// Render Markdown
const mdRef: Ref<HTMLElement | undefined> = ref();
watch(props, (props) => {
  // When parent component gets the model card info, then update the markdown to show
  if (!mdRef.value) {
    return;
  }
  mdRef.value.innerHTML = DOMPurify.sanitize(md.render(props.markdown));
  for (const data of chartData) {
    let selector = document.getElementById(data.id ?? '');
    if (!selector) {
      continue;
    }
    Plotly.newPlot(selector, data.data, data.layout, {
      responsive: true,
    });
  }
  hljs.highlightAll();
});
</script>
