import { AxiosError } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export const useUploadStore = defineStore('users', {
  state: () => ({}),
  actions: {
    async uploadVideo(videoFile: File) {
      const form = new FormData();
      form.append('video', videoFile[0]);
      await api
        .post('/buckets/video', form)
        .then((data) => {
          console.log(data.data.video_location);
        })
        .catch((err) => {
          Notify.create({
            message: 'Video upload failed.',
            type: 'negative',
          });
        });
    },
  },
});
