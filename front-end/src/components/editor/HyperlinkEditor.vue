<template>
  <q-card>
    <q-card-section>
      <div class="text-h5">
        Set Hyperlink for `{{
          editor.view.state.selection.$head.parent.textContent
        }}`
      </div>
    </q-card-section>
    <q-card-section>
      <q-input outlined v-model="url" label="URL" min="0"></q-input>
    </q-card-section>
    <q-card-actions>
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        label="Set Hyperlink"
        color="primary"
        @click="setHyperlink"
        v-close-popup
      ></q-btn>
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        label="Unlink Text"
        color="primary"
        @click="
          () => {
            url = '';
            setHyperlink();
          }
        "
        v-close-popup
      ></q-btn>
      <q-btn
        no-caps
        rounded
        padding="sm xl"
        label="Cancel"
        color="red"
        v-close-popup
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { Notify } from 'quasar';
import { ref } from 'vue';
import { Editor } from '@tiptap/vue-3';

export interface HyperlinkEditorProps {
  editor: Editor;
  defaultURL?: string;
}

const props = withDefaults(defineProps<HyperlinkEditorProps>(), {
  defaultURL: '',
});

const url = ref(props.editor.getAttributes('link').href || props.defaultURL);

const setHyperlink = () => {
  // If empty, remove the link
  if (url.value === '') {
    props.editor.chain().focus().unsetLink().run();
    Notify.create({
      message: 'Hyperlink removed',
      color: 'positive',
    });
  } else {
    // Otherwise, set the link to the URL
    props.editor.chain().focus().setLink({ href: url.value }).run();
    Notify.create({
      message: `Hyperlink set to ${url.value}`,
      color: 'positive',
    });
  }
};
</script>
