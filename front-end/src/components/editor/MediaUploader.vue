<template>
  <q-card>
    <q-card-section>
      <div class="text-h5">Upload Media File</div>
    </q-card-section>
    <q-card-section>
      <q-file
        rounded
        outlined
        padding="sm xl"
        v-model="uploadStore.files"
        :accept="accept"
        :max-size="maxTotalSize"
        :multiple="multiple"
        :max-files="maxFiles"
        :label="label"
        filled
      ></q-file>
    </q-card-section>
    <q-card-actions>
      <q-btn
        label="Upload"
        color="primary"
        @click="onUpload"
        v-close-popup
        rounded
        no-caps
        padding="sm xl"
      ></q-btn>
      <q-btn
        label="Cancel"
        color="red"
        rounded
        no-caps
        padding="sm xl"
        v-close-popup
      ></q-btn>
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { Editor } from '@tiptap/vue-3';
import { Notify } from 'quasar';
import { useUploadStore } from 'src/stores/upload-store';
export interface MediaUploaderProps {
  editor: Editor;
  uploadEndpoint: string;
  accept: string;
  maxTotalSize: number;
  multiple: boolean;
  maxFiles?: number;
  fieldName?: string | ((file: File) => string);
  label?: string;
}

const props = withDefaults(defineProps<MediaUploaderProps>(), {
  accept: 'image/*',
  maxTotalSize: 5242880, // 5MB
  multiple: true,
  maxFiles: 50,
  label: 'Upload Image (Max 5MB Size)',
  uploadEndpoint: '/upload/media',
  fieldName: 'files',
});

const uploadStore = useUploadStore();

const onUpload = () => {
  uploadStore.files.forEach((file) => {
    // Convert to base64
    // will store in serverside in s3 storage
    // where the src will be replaced with the s3 url
    uploadStore
      .toBase64(file)
      .then((base64) => {
        // Add to editor
        props.editor
          .chain()
          .focus()
          .setImage({ src: base64, alt: file.name })
          .goToNextCell()
          .run();
      })
      .catch((err) => {
        Notify.create({
          message: 'Error uploading file',
          color: 'negative',
        });
        console.error(err);
      });
  });

  uploadStore.clearFiles();
};
</script>
