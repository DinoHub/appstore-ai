<template>
  <!-- Use tiptap to render.-->
  <!-- We do not re-use the editor component due to some issues faced with the watch callback -->
  <!-- TODO: Check if the issues are still there to avoid re-use of code -->
  <!-- or consider an if-else statement on watcher to see if that works -->
  <editor-content class="text-left q-pl-md" :editor="editor" />
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3';

import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import Placeholder from '@tiptap/extension-placeholder';
import Table from '@tiptap/extension-table';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import Image from '@tiptap/extension-image';
import Chart from 'src/plugins/tiptap-charts';

import 'highlight.js/lib/common';
import css from 'highlight.js/lib/languages/css';
import js from 'highlight.js/lib/languages/javascript';
import ts from 'highlight.js/lib/languages/typescript';
import html from 'highlight.js/lib/languages/xml';
import python from 'highlight.js/lib/languages/python';

import { lowlight } from 'lowlight';

import { ref, watch } from 'vue';

export interface TiptapDisplayProps {
  content?: string;
}

// Register languages for code highlighting
lowlight.registerLanguage('css', css);
lowlight.registerLanguage('js', js);
lowlight.registerLanguage('ts', ts);
lowlight.registerLanguage('html', html);
lowlight.registerLanguage('python', python);

const props = defineProps<TiptapDisplayProps>();
const content = ref(props.content ?? '');
const editor = useEditor({
  extensions: [
    Chart,
    StarterKit,
    Underline,
    Placeholder,
    CodeBlockLowlight.configure({
      lowlight,
    }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableHeader,
    TableCell,
    Image.configure({
      allowBase64: true,
    }),
  ],
  content: props.content ?? 'Type here...',
  editable: false,
});

watch(
  () => props.content,
  (newContent) => {
    if (newContent !== content.value) {
      content.value = newContent ?? '';
      editor.value?.chain().setContent(content.value).run();
    }
  },
);
</script>

<style lang="scss">
@import '../../css/markup.scss';
</style>
