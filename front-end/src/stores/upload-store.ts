import { AxiosError, AxiosResponse } from 'axios';
import { Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import { useModelStore } from './model-store';

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
    /**
     * Uploads a video to the server and returns the URL
     * @param videoFile Video file to upload
     * @returns Promise that resolves to the location of the uploaded video
     */
    async uploadVideo(videoFile: File): Promise<string> {
      const form = new FormData();
      form.append('video', videoFile[0]);
      let videoLocation = '';
      console.log(form);
      await api
        .post('buckets/video', form, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then((data) => {
          videoLocation = data.data.video_location;
        })
        .catch((err) => {
          console.error(err);
          Notify.create({
            message: 'Video upload failed.',
            type: 'negative',
          });
        });
      return videoLocation;
    },
    /**
     * Replaces a video on the server and returns the URL
     * @param videoFile Video file to upload
     * @param userId user Id of model card to update
     * @param modelId  model Id of model card to update
     * @returns Promise that resolves to the location of the uploaded video
     */
    async replaceVideo(
      videoFile: File,
      userId: string,
      modelId: string
    ): Promise<string> {
      const modelStore = useModelStore();
      const form = new FormData();
      form.append('new_video', videoFile[0]);
      form.append('userId', userId);
      form.append('modelId', modelId);
      let videoLocation = '';
      await api
        .put('/buckets/video', form, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then((data) => {
          videoLocation = data.data.video_location;
          modelStore.updateModel(
            { videoLocation: videoLocation },
            userId,
            modelId
          );
          Notify.create({
            message: 'Video replaced successfullly!',
            type: 'positive',
          });
        })
        .catch((err) => {
          console.error(err);
          Notify.create({
            message: 'Video upload failed.',
            type: 'negative',
          });
        });
      return videoLocation;
    },
    // Unsure if this function isneeded
    async uploadMedia(
      url: string,
      fieldName: string | ((file: File) => string)
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
    /**
     * Converts a file to base64 string
     * @param file File to convert to base64
     * @returns The base64 string of the file
     */
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
