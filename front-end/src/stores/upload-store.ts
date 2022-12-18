import { AxiosError } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export const useUploadStore = defineStore('users', {
  state: () => ({}),
  actions: {
    async uploadVideo(videoFile: File) {
      console.log(videoFile[0]);
      const form = new FormData();
      form.append('video', videoFile[0]);
      api.post('/upload/video', form);
    },
  },
});
