<template>
  <!-- Editor Toolbar -->
  <div v-if="editor">
    <q-bar class="bg-white">
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
        icon="looks_one"
        @click="editor?.chain().focus().setHeading({ level: 1 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 2 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 2 }) ?? true)"
        icon="looks_two"
        @click="editor?.chain().focus().setHeading({ level: 2 }).run()"
      />
      <q-btn
        dense
        :text-color="
          _iconFill(editor?.isActive('heading', { level: 3 }) ?? true)
        "
        :color="_buttonBg(editor?.isActive('heading', { level: 3 }) ?? true)"
        icon="looks_3"
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
      <!-- Chart Editor -->
      <q-btn dense icon="insert_chart" @click="chartEditor = true" />
      <q-dialog v-model="chartEditor">
        <q-card>
          <q-card-section>
            <div class="text-h5">Chart Editor</div>
            <div>
              <div>
                <!-- Editor -->
              </div>
              <figure class="col">
                <!-- Preview -->
                <span class="text-h6">Preview</span>
              </figure>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>
      <!-- Show Source Code -->
      <q-btn label="Show Source Code" dense @click="showSource = true"></q-btn>
      <q-dialog v-model="showSource">
        <q-card>
          <q-card-section>
            <pre>
              <code class="language-html">
            {{ editor?.getHTML() }}
              </code>
            </pre>
          </q-card-section>
        </q-card>
      </q-dialog>
    </q-bar>
    <editor-content
      class="text-left"
      @click="editor?.commands.focus()"
      :editor="editor"
    />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import css from 'highlight.js/lib/languages/css';
import js from 'highlight.js/lib/languages/javascript';
import ts from 'highlight.js/lib/languages/typescript';
import html from 'highlight.js/lib/languages/xml';
import python from 'highlight.js/lib/languages/python';

import { lowlight } from 'lowlight';

import { ref, watch } from 'vue';

lowlight.registerLanguage('css', css);
lowlight.registerLanguage('js', js);
lowlight.registerLanguage('ts', ts);
lowlight.registerLanguage('html', html);
lowlight.registerLanguage('python', python);

const editor = useEditor({
  extensions: [
    StarterKit,
    Underline,
    CodeBlockLowlight.configure({
      lowlight,
    }),
  ],
  content: `<p>Hello World! 🌍</p><pre><code class="language-javascript">for (var i=1; i <= 20; i++)
{
  if (i % 15 == 0)
    console.log("FizzBuzz");
  else if (i % 3 == 0)
    console.log("Fizz");
  else if (i % 5 == 0)
    console.log("Buzz");
  else
    console.log(i);
}</code></pre>`,
});

const showSource = ref(false);
const chartEditor = ref(false);

function _buttonBg(condition: boolean) {
  return condition ? 'primary' : 'white';
}

function _iconFill(condition: boolean) {
  return condition ? 'white' : 'black';
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
</style>
