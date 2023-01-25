<template>
  <!-- Editor Toolbar -->
  <!-- TODO: Make each button+dialog menu a component-->
  <!-- TODO: Move logic e.g add table to component. See HyperlinkEditor component for example on how this is to be done-->
  <div v-if="editor" style="overflow: none">
    <q-toolbar
      v-if="props.editable"
      class="q-gutter-sm row"
      style="flex-wrap: wrap !important"
    >
      <!-- Bold -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('bold') ?? true)"
        :color="_buttonBg(editor?.isActive('bold') ?? true)"
        icon="format_bold"
        @click="editor?.chain().focus().toggleBold().run()"
      />
      <!-- Italic -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('italic') ?? true)"
        :color="_buttonBg(editor?.isActive('italic') ?? true)"
        icon="format_italic"
        @click="editor?.chain().focus().toggleItalic().run()"
      />
      <!-- Underline -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('underline') ?? true)"
        :color="_buttonBg(editor?.isActive('underline') ?? true)"
        icon="format_underline"
        @click="editor?.chain().focus().toggleUnderline().run()"
      />
      <!-- Strike -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('strike') ?? true)"
        :color="_buttonBg(editor?.isActive('strike') ?? true)"
        icon="format_strikethrough"
        @click="editor?.chain().focus().toggleStrike().run()"
      />
      <!-- Hyperlink-->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('link') ?? true)"
        :color="_buttonBg(editor?.isActive('link') ?? true)"
        icon="link"
        @click="hyperlink = true"
      ></q-btn>

      <!-- Code Block -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('codeBlock') ?? true)"
        :color="_buttonBg(editor?.isActive('codeBlock') ?? true)"
        icon="code"
        @click="editor?.chain().focus().toggleCodeBlock().run()"
      />
      <!-- H1-H3 -->
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 1 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 1 }) ?? true)"
        label="H1"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
        label="H2"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
        label="H3"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
      />
      <!-- Bullet List -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('bulletList') ?? true)"
        :color="_buttonBg(editor?.isActive('bulletList') ?? true)"
        icon="format_list_bulleted"
        @click="editor?.chain().focus().toggleBulletList().run()"
      />
      <!-- Ordered List -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('orderedList') ?? true)"
        :color="_buttonBg(editor?.isActive('orderedList') ?? true)"
        icon="format_list_numbered"
        @click="editor?.chain().focus().toggleOrderedList().run()"
      />
      <!-- Add Image -->
      <q-btn
        dense
        :text-color="_iconFill(editor?.isActive('image') ?? true)"
        :color="_buttonBg(editor?.isActive('image') ?? true)"
        icon="image"
        @click="imageUploader = true"
      ></q-btn>
      <q-dialog v-model="imageUploader">
        <media-uploader :editor="editor"> </media-uploader>
      </q-dialog>
      <!-- Table Editor -->
      <q-btn
        :text-color="_iconFill(editor?.isActive('table') ?? true)"
        :color="_buttonBg(editor?.isActive('table') ?? true)"
        dense
        icon="table_chart"
        @click="tableCreator = true"
      >
      </q-btn>
      <q-dialog v-model="tableCreator">
        <table-creator :editor="editor" />
      </q-dialog>
      <!-- Chart Editor -->
      <q-btn
        :text-color="_iconFill(editor?.isActive('chart') ?? true)"
        :color="_buttonBg(editor?.isActive('chart') ?? true)"
        dense
        icon="insert_chart"
        @click="chartEditor = true"
      />
      <q-dialog persistent full-width v-model="chartEditor">
        <plotly-editor
          @new-plot="(data, layout) => insertChart(editor, data, layout)"
        ></plotly-editor>
      </q-dialog>
      <!-- Show Source Code -->
      <q-btn
        icon="html"
        :text-color="_iconFill(showSource)"
        :color="_buttonBg(showSource)"
        dense
        @click="showSource = true"
      ></q-btn>
      <q-dialog v-model="showSource">
        <q-card>
          <q-card-section>
            <div class="title-large">Source Code</div>
          </q-card-section>
          <q-card-section>
            <!-- <highlightjs
              language="html"
              :code="content"
            ></highlightjs> -->
            <code>
              {{ content }}
            </code>
          </q-card-section>
        </q-card>
      </q-dialog>
      <!-- Hyperlink Editor -->
      <q-dialog v-model="hyperlink">
        <hyperlink-editor :editor="editor"></hyperlink-editor>
      </q-dialog>
      <slot name="toolbar"></slot>
    </q-toolbar>
    <main>
      <editor-content
        class="text-left q-pl-md"
        @click="editor?.commands.focus()"
        :editor="editor"
      />
    </main>
    <aside v-if="props.editable">
      <bubble-menu
        class="q-gutter-xs row"
        :tippy-options="{ duration: 180 }"
        :editor="editor"
      >
        <!-- Bold -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('bold') ?? true)"
          :color="_buttonBg(editor?.isActive('bold') ?? true)"
          icon="format_bold"
          @click="editor?.chain().focus().toggleBold().run()"
        />
        <!-- Italic -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('italic') ?? true)"
          :color="_buttonBg(editor?.isActive('italic') ?? true)"
          icon="format_italic"
          @click="editor?.chain().focus().toggleItalic().run()"
        />
        <!-- Underline -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('underline') ?? true)"
          :color="_buttonBg(editor?.isActive('underline') ?? true)"
          icon="format_underline"
          @click="editor?.chain().focus().toggleUnderline().run()"
        />
        <!-- Strike -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('strike') ?? true)"
          :color="_buttonBg(editor?.isActive('strike') ?? true)"
          icon="format_strikethrough"
          @click="editor?.chain().focus().toggleStrike().run()"
        />

        <!-- Hyperlink-->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('link') ?? true)"
          :color="_buttonBg(editor?.isActive('link') ?? true)"
          icon="link"
          @click="hyperlink = true"
        ></q-btn>
        <!-- Code Block -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('codeBlock') ?? true)"
          :color="_buttonBg(editor?.isActive('codeBlock') ?? true)"
          icon="code"
          @click="editor?.chain().focus().toggleCodeBlock().run()"
        />
        <!-- H1-H3 -->
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 1 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 1 }) ?? true)"
          label="H1"
          @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        />
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
          label="H2"
          @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        />
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
          label="H3"
          @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        />
        <!-- Bullet List -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('bulletList') ?? true)"
          :color="_buttonBg(editor?.isActive('bulletList') ?? true)"
          icon="format_list_bulleted"
          @click="editor?.chain().focus().toggleBulletList().run()"
        />
        <!-- Ordered List -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('orderedList') ?? true)"
          :color="_buttonBg(editor?.isActive('orderedList') ?? true)"
          icon="format_list_numbered"
          @click="editor?.chain().focus().toggleOrderedList().run()"
        />
        <!-- Image -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('image') ?? true)"
          :color="_buttonBg(editor?.isActive('image') ?? true)"
          icon="image"
          @click="imageUploader = true"
        ></q-btn>
      </bubble-menu>
      <floating-menu
        class="q-gutter-xs row"
        :tippy-options="{ duration: 100 }"
        :editor="editor"
      >
        <!-- H1-H3 -->
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 1 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 1 }) ?? true)"
          label="H1"
          @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        />
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
          label="H2"
          @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        />
        <q-btn
          dense
          :text-color="
            _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
          "
          :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
          label="H3"
          @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        />
        <!-- Code Block -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('codeBlock') ?? true)"
          :color="_buttonBg(editor?.isActive('codeBlock') ?? true)"
          icon="code"
          @click="editor?.chain().focus().toggleCodeBlock().run()"
        />
        <!-- Bullet List -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('bulletList') ?? true)"
          :color="_buttonBg(editor?.isActive('bulletList') ?? true)"
          icon="format_list_bulleted"
          @click="editor?.chain().focus().toggleBulletList().run()"
        />
        <!-- Ordered List -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('orderedList') ?? true)"
          :color="_buttonBg(editor?.isActive('orderedList') ?? true)"
          icon="format_list_numbered"
          @click="editor?.chain().focus().toggleOrderedList().run()"
        />
        <!-- Add Image -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('image') ?? true)"
          :color="_buttonBg(editor?.isActive('image') ?? true)"
          icon="image"
          @click="imageUploader = true"
        ></q-btn>
        <!-- Chart Editor -->
        <q-btn
          dense
          :text-color="_iconFill(editor?.isActive('image') ?? true)"
          :color="_buttonBg(editor?.isActive('image') ?? true)"
          icon="insert_chart"
          @click="chartEditor = true"
        />
      </floating-menu>
    </aside>
  </div>
</template>

<script setup lang="ts">
import {
  useEditor,
  Editor,
  EditorContent,
  BubbleMenu,
  FloatingMenu,
} from '@tiptap/vue-3';

import PlotlyEditor from './PlotlyEditor.vue';
import TableCreator from './TableCreator.vue';
import HyperlinkEditor from './HyperlinkEditor.vue';
import MediaUploader from './MediaUploader.vue';

import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import Placeholder from '@tiptap/extension-placeholder';
import Table from '@tiptap/extension-table';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import Chart from 'src/plugins/tiptap-charts';

import 'highlight.js/lib/common';
import hljsVuePlugin from '@highlightjs/vue-plugin';
import css from 'highlight.js/lib/languages/css';
import js from 'highlight.js/lib/languages/javascript';
import ts from 'highlight.js/lib/languages/typescript';
import html from 'highlight.js/lib/languages/xml';
import python from 'highlight.js/lib/languages/python';

import { lowlight } from 'lowlight';

import { ref, watch } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';

export interface TiptapEditorProps {
  content?: string;
  editable?: boolean;
  replaceContent?: boolean;
}
const highlightjs = hljsVuePlugin.component;

// Register languages for code highlighting
lowlight.registerLanguage('css', css);
lowlight.registerLanguage('js', js);
lowlight.registerLanguage('ts', ts);
lowlight.registerLanguage('html', html);
lowlight.registerLanguage('python', python);

const props = defineProps<TiptapEditorProps>();
const emit = defineEmits(['update:content', 'replaced-content']);
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
    Link,
  ],
  content: props.content ?? 'Type here...',
  onUpdate({ editor }) {
    content.value = editor.getHTML();
    emit('update:content', content.value);
  },
  editable: props.editable ?? false,
});

const showSource = ref(false);
const chartEditor = ref(false);
const tableCreator = ref(false);
const imageUploader = ref(false);
const hyperlink = ref(false);

const _buttonBg = (condition: boolean) => (condition ? 'primary' : 'white');

const _iconFill = (condition: boolean) => (condition ? 'white' : 'black');

const insertChart = (
  editor: Editor,
  data: Record<string, any>[],
  layout: Record<string, any>,
) =>
  editor
    ?.chain()
    .focus()
    .insertContent({
      type: 'chart',
      attrs: {
        layout: JSON.stringify(layout),
        data: JSON.stringify(data),
      },
    })
    .run();

watch(props, (newVal) => {
  // ensure that we can replace the content from outside
  // this is used to populate card descriptions
  if (props.replaceContent && newVal.content) {
    content.value = newVal.content;
    editor.value?.chain().setContent(content.value).run();
    emit('update:content', content.value); // emit the new content
    emit('replaced-content'); // set props.replaceContent to false after this
  }
});
</script>
<style lang="scss">
@import '../../css/markup.scss';
</style>
