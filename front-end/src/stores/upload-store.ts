import { AxiosError, AxiosResponse } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';

export interface MediaUploadResponse {
  files: {
    url: string;
    name: string;
  }[];
}

export const useUploadStore = defineStore('users', {
  state: () => ({
    files: [] as File[],
  }),
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
    async uploadMedia(
      url: string,
      fieldName: string | ((file: File) => string),
    ): Promise<MediaUploadResponse> {
      const form = new FormData();
      for (const media of this.files) {
        const name =
          typeof fieldName === 'function' ? fieldName(media) : fieldName;
        form.append(name, media, media.name);
      }
      const res = await api.post(url, form);
      return res.data;
    },
    async toBase64(file: File): Promise<string> {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = (error) => reject(error);
      });
    },
    clearFiles() {
      this.files = [];
    },
  },
});