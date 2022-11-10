<style scoped>
.sticky {
  position: sticky;
  top: 0;
}
</style>
<template>
  <!-- Editor Toolbar -->
  <div v-if="editor" style="overflow: none">
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
        @click="editor?.chain().focus().setHeading({ level: 1 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
        label="H2"
        @click="editor?.chain().focus().setHeading({ level: 2 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
        label="H3"
        @click="editor?.chain().focus().setHeading({ level: 3 }).run()"
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
        @click="editor?.chain().focus().setHeading({ level: 1 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
        label="H2"
        @click="editor?.chain().focus().setHeading({ level: 2 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
        label="H3"
        @click="editor?.chain().focus().setHeading({ level: 3 }).run()"
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
      <q-btn dense icon="insert_chart" @click="chartEditor = true" />
    </floating-menu>
    <aside class="bg-white q-gutter-sm row">
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
        @click="editor?.chain().focus().setHeading({ level: 1 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
        label="H2"
        @click="editor?.chain().focus().setHeading({ level: 2 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
        label="H3"
        @click="editor?.chain().focus().setHeading({ level: 3 }).run()"
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
        <q-uploader
          label="Upload Image (up to 5mb)"
          accept=".jpg, image/*"
          max-total-size="5242880"
          :factory="uploadMedia"
          @uploaded="addMedia"
        >
        </q-uploader>
      </q-dialog>
      <!-- Chart Editor -->
      <q-btn dense icon="insert_chart" @click="chartEditor = true" />
      <q-dialog persistent full-width v-model="chartEditor">
        <plotly-editor
          @new-plot="(data, layout) => insertChart(editor, data, layout)"
        ></plotly-editor>
      </q-dialog>
      <!-- Show Source Code -->
      <q-btn
        label="Show Source Code"
        dense
        @click="
          () => {
            displaySourceCode(editor);
          }
        "
      ></q-btn>
      <q-dialog v-model="showSource">
        <q-card>
          <q-card-section>
            <pre>
                <code id="source" class="language-html">
                </code>
              </pre>
          </q-card-section>
        </q-card>
      </q-dialog>
    </aside>
    <editor-content
      class="text-left q-pl-md"
      @click="editor?.commands.focus()"
      :editor="editor"
    />
  </div>
</template>

<script setup lang="ts">
import {
  useEditor,
  EditorContent,
  BubbleMenu,
  FloatingMenu,
} from '@tiptap/vue-3';

import PlotlyEditor from './PlotlyEditor.vue';

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

import hljs from 'highlight.js';
import css from 'highlight.js/lib/languages/css';
import js from 'highlight.js/lib/languages/javascript';
import ts from 'highlight.js/lib/languages/typescript';
import html from 'highlight.js/lib/languages/xml';
import python from 'highlight.js/lib/languages/python';

import { lowlight } from 'lowlight';

import { ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';

lowlight.registerLanguage('css', css);
lowlight.registerLanguage('js', js);
lowlight.registerLanguage('ts', ts);
lowlight.registerLanguage('html', html);
lowlight.registerLanguage('python', python);

export interface Props {
  content?: string;
}

const props = defineProps<Props>();
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
});

const showSource = ref(false);
const chartEditor = ref(false);
const imageUploader = ref(false);

function _buttonBg(condition: boolean) {
  return condition ? 'primary' : 'white';
}

function _iconFill(condition: boolean) {
  return condition ? 'white' : 'black';
}

function insertChart(
  editor: Editor,
  data: Record<string, any>[],
  layout: Record<string, any>,
) {
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
}

function uploadMedia(file) {
  return new Promise((resolve, reject) => {
    // Get Token
    const authStore = useAuthStore();
    resolve({
      url: process.env.backendAPI + '/media/upload',
      method: 'POST',
      headers: [
        { name: 'Authorization', value: `Bearer ${authStore.access_token}` },
      ],
      withCredentials: true,
    });
  });
}

function addMedia({ files, xhr }) {
  // Add uploaded images to Editor
}

function displaySourceCode(editor: Editor) {
  // TODO: FIX THIS
  showSource.value = true;
  const select = document.getElementById('source');
  if (select) {
    select.innerHTML = editor.getHTML();
    console.log(select.innerHTML);
    hljs.highlightAll();
  } else {
    console.warn('Cannot find!');
  }
}
</script>
<style lang="scss">
/* Basic editor styles */
.ProseMirror {
  > * + * {
    margin-top: 0.75em;
  }

  pre {
    background: #0d0d0d;
    color: #fff;
    font-family: 'JetBrainsMono', monospace;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;

    code {
      color: inherit;
      padding: 0;
      background: none;
      font-size: 0.8rem;
    }

    .hljs-comment,
    .hljs-quote {
      color: #616161;
    }

    .hljs-variable,
    .hljs-template-variable,
    .hljs-attribute,
    .hljs-tag,
    .hljs-name,
    .hljs-regexp,
    .hljs-link,
    .hljs-name,
    .hljs-selector-id,
    .hljs-selector-class {
      color: #f98181;
    }

    .hljs-number,
    .hljs-meta,
    .hljs-built_in,
    .hljs-builtin-name,
    .hljs-literal,
    .hljs-type,
    .hljs-params {
      color: #fbbc88;
    }

    .hljs-string,
    .hljs-symbol,
    .hljs-bullet {
      color: #b9f18d;
    }

    .hljs-title,
    .hljs-section {
      color: #faf594;
    }

    .hljs-keyword,
    .hljs-selector-tag {
      color: #70cff8;
    }

    .hljs-emphasis {
      font-style: italic;
    }

    .hljs-strong {
      font-weight: 700;
    }
  }
}

.ProseMirror {
  table {
    border-collapse: collapse;
    table-layout: fixed;
    width: 100%;
    margin: 0;
    overflow: hidden;

    td,
    th {
      min-width: 1em;
      border: 2px solid #ced4da;
      padding: 3px 5px;
      vertical-align: top;
      box-sizing: border-box;
      position: relative;

      > * {
        margin-bottom: 0;
      }
    }

    th {
      font-weight: bold;
      text-align: left;
      background-color: #f1f3f5;
    }

    .selectedCell:after {
      z-index: 2;
      position: absolute;
      content: '';
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      background: rgba(200, 200, 255, 0.4);
      pointer-events: none;
    }

    .column-resize-handle {
      position: absolute;
      right: -2px;
      top: 0;
      bottom: -2px;
      width: 4px;
      background-color: #adf;
      pointer-events: none;
    }

    p {
      margin: 0;
    }
  }
}

.tableWrapper {
  padding: 1rem 0;
  overflow-x: auto;
}

.resize-cursor {
  cursor: ew-resize;
  cursor: col-resize;
}
</style>
