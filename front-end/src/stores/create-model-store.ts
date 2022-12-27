import { ModelCard, ModelCardNoInference, useModelStore } from './model-store';

import { Chart, EnvField } from 'src/components/models';
import { Notify } from 'quasar';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { useExperimentStore } from './experiment-store';
import { useInferenceServiceStore } from './inference-service-store';
import { useUploadStore } from './upload-store';
import { create } from 'domain';

export const useCreationStore = defineStore('createModel', {
  state: () => {
    return {
      step: 1 as number,
      tags: [] as string[],
      frameworks: [] as string[],
      modelPath: '' as string,
      experimentPlatform: '' as string, // todo: enum
      experimentID: '' as string,
      datasetPlatform: '' as string,
      datasetID: '' as string,
      modelName: '' as string,
      modelTask: '' as string,
      modelOwner: '' as string,
      modelPOC: '' as string,
      modelDesc: '' as string,
      modelExplain: '' as string,
      modelUsage: '' as string,
      modelLimitations: '' as string,
      markdownContent: `<h3>Description <a id="description"></a></h3>
      <hr>
      <p><strong>EXAMPLE:</strong></p>
      <p><span style="font-family: 'trebuchet ms', geneva, sans-serif;">The general description of your model, usually a summary paragraph that can give developers a good idea of the purpose of said model. Additionally other things like metrics used/best scores can be posted in tables or other formats too if desired.&nbsp;</span></p>
      <table style="border-collapse: collapse; width: 46.8289%; height: 164px; background-color: rgb(194, 224, 244); border: 1px solid rgb(126, 140, 141); margin-left: auto; margin-right: auto;" border="1"><colgroup><col style="width: 65.8868%;"><col style="width: 34.1157%;"></colgroup>
      <tbody>
      <tr style="height: 25.2px;">
      <td style="border-width: 1px; height: 25.2px; background-color: rgb(53, 152, 219); text-align: center; border-color: rgb(126, 140, 141);"><span style="color: rgb(236, 240, 241);"><strong>Metrics Used</strong></span></td>
      <td style="border-width: 1px; height: 25.2px; background-color: rgb(53, 152, 219); text-align: center; border-color: rgb(126, 140, 141);"><span style="color: rgb(236, 240, 241);"><strong>Best Score</strong></span></td>
      </tr>
      <tr style="height: 25.2px;">
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">Metric 1</td>
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">24.96</td>
      </tr>
      <tr style="height: 25.2px;">
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">Metric 2</td>
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">22.2</td>
      </tr>
      <tr style="height: 25.2px;">
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">Metric 3</td>
      <td style="border-width: 1px; height: 25.2px; text-align: center; border-color: rgb(126, 140, 141);">23.2</td>
      </tr>
      </tbody>
      </table>
      <p><span style="font-family: 'trebuchet ms', geneva, sans-serif;"><strong><em>(Example Text to Replace)</em></strong></span></p>
      <p>&nbsp;</p>
      <h3>Explanation <a id="explanation"></a></h3>
      <hr>
      <p><strong>EXAMPLE:</strong></p>
      <p>This section should explain the model.</p>
      <p dir="ltr">Description may include:</p>
      <ol style="list-style-type: lower-alpha;">
      <li dir="ltr"><em><strong>general logic</strong></em> &ndash; what are the key features that matter and how are they related?</li>
      <li dir="ltr"><em><strong>particular inferences </strong></em>&ndash; are specific predictions explained?&nbsp;</li>
      <li dir="ltr"><em><strong>nature </strong></em>&ndash; are explanations in the form of associations (e.g., feature importance), contrasts (e.g., counterfactuals), or causal models?</li>
      <li dir="ltr"><em><strong>medium </strong></em>&ndash;are they provided as text, visuals or some other format?</li>
      <li dir="ltr"><em><strong>audience </strong></em>&ndash; which user personas are they meant for?</li>
      <li dir="ltr"><em><strong>motivation</strong></em> &ndash; why were this nature and medium chosen for this audience?</li>
      </ol>
      <p><span style="font-family: 'trebuchet ms', geneva, sans-serif;"><strong><em>(Example Text to Replace)</em></strong></span></p>
      <p>&nbsp;</p>
      <h3>Model Usage <a id="model_use"></a></h3>
      <hr>
      <p><strong>EXAMPLE:</strong></p>
      <p>What task the model is used on, whether it's meant for downstream tasks, what genre or type of data it can be used on, etc.</p>
      <p>You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task. See the model hub to look for fine-tuned versions on a task that interests you.</p>
      <p>Random formula: x<sup>2</sup> + &pi;</p>
      <pre class="language-python"><code>print('hello world!')</code></pre>
      <p>Note that this model is primarily aimed at being fine-tuned on tasks that use the whole sentence (potentially masked) to make decisions, such as sequence classification, token classification or question answering. For tasks such as text generation you should look at model like GPT2.&nbsp;</p><p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>
      <p>&nbsp;</p>
      <h3>Limitations <a id="limitations"></a></h3>
      <hr>
      <p><strong>EXAMPLE:</strong></p>
      <p>The limitation or issues that the model may possible, any biases towards certain types of data, etc.</p>
      <blockquote>
      <p><strong>"I think, therefore I am" -Ren&eacute; Descartes</strong></p>
      </blockquote>
      <p>The training data used for this model contains a lot of unfiltered content from the internet, which is far from neutral. Therefore, the model can have biased predictions.</p> <p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>` as string,
      performanceMarkdown:
        '<h3>Performance</h3><hr><ul><li><p>This is an example graph showcasing how the graph option works! Use the button on the toolbar to create new graphs. You can also edit preexisting graphs using the edit button! </p></li></ul><chart data-layout="{&quot;title&quot;:{&quot;text&quot;:&quot;Example Graph&quot;},&quot;xaxis&quot;:{&quot;title&quot;:{&quot;text&quot;:&quot;Values&quot;},&quot;type&quot;:&quot;linear&quot;,&quot;range&quot;:[0.6391275611368142,7.360872438863185],&quot;autorange&quot;:true},&quot;yaxis&quot;:{&quot;title&quot;:{&quot;text&quot;:&quot;Values&quot;},&quot;type&quot;:&quot;linear&quot;,&quot;range&quot;:[5.6050955414012735,74.39490445859873],&quot;autorange&quot;:true}}" data-data="[{&quot;x&quot;:[1,2,3,4,5,6,7,8,9,10],&quot;y&quot;:[10,20,30,40,50,60,70],&quot;type&quot;:&quot;scatter&quot;}]"></chart>' as string,
      plots: [] as Chart[],
      imageUri: '' as string,
      containerPort: undefined as number | undefined,
      serviceName: '' as string,
      previewServiceName: null as string | null,
      previewServiceUrl: null as string | null,
      exampleVideo: undefined as File | undefined,
      env: [] as EnvField[],
    };
  },
  getters: {
    noServiceMetadataValid(): boolean {
      // Redundant?
      const keys = Object.keys(this).filter((item) =>
        [
          'tags',
          'frameworks',
          'performanceMarkdown',
          'markdownContent',
          'modelName',
          'modelPath',
          'modelTask',
          'modelDesc',
          'modelExplain',
          'modelUsage',
          'modelLimitations',
          'exampleVideo',
        ].includes(item)
      );
      console.warn(`Keys: ${JSON.stringify(keys)}`);
      if (
        (this.datasetID == '' && this.datasetPlatform != '') ||
        (this.experimentID == '' && this.experimentPlatform != '')
      ) {
        return false;
      }
      for (const key of keys) {
        if (typeof this[key] == 'object') {
          if (this[key].length == 0) {
            return false;
          }
        } else if (typeof this[key] == 'string') {
          if (this[key] == '') {
            return false;
          }
        }
      }
      return true;
    },
    metadataValid(): boolean {
      const keys = Object.keys(this).filter((item) =>
        [
          'tags',
          'frameworks',
          'performanceMarkdown',
          'markdownContent',
          'modelName',
          'modelPath',
          'modelTask',
          'modelDesc',
          'modelExplain',
          'modelUsage',
          'modelLimitations',
        ].includes(item)
      );
      console.warn(`Keys: ${JSON.stringify(keys)}`);
      if (
        (this.datasetID == '' && this.datasetPlatform != '') ||
        (this.experimentID == '' && this.experimentPlatform != '')
      ) {
        return false;
      }
      for (const key of keys) {
        if (typeof this[key] == 'object') {
          if (this[key].length == 0) {
            return false;
          }
        } else if (typeof this[key] == 'string') {
          if (this[key] == '') {
            return false;
          }
        }
      }
      return true;
    },
    uniqueEnv(): Record<string, string> {
      const uniqueEnvs: Record<string, string> = {};
      this.env.forEach(({ key, value }) => {
        uniqueEnvs[key] = value;
      });
      return uniqueEnvs;
    },
  },
  actions: {
    async loadMetadataFromExperiment(): Promise<void> {
      if (!this.experimentID || !this.experimentPlatform) {
        return Promise.reject();
      }
      const experimentStore = useExperimentStore();
      try {
        const metadata = await experimentStore.getExperimentByID(
          this.experimentID,
          this.experimentPlatform
        );
        this.tags = Array.from(new Set([...this.tags, ...metadata.tags]));
        this.frameworks = Array.from(
          new Set([...this.frameworks, ...metadata.frameworks])
        );
      } catch (error) {
        return Promise.reject(error);
      }
    },
    async launchPreviewService(modelId: string): Promise<void> {
      const inferenceServiceStore = useInferenceServiceStore();
      try {
        const { serviceName, inferenceUrl } =
          await inferenceServiceStore.launchPreviewService(
            modelId,
            this.imageUri,
            this.containerPort,
            this.uniqueEnv
          );
        this.previewServiceUrl = inferenceUrl;
        this.previewServiceName = serviceName; // save so we know what to clean up
      } catch (error) {
        return Promise.reject(error);
      }
    },
    async createModel() {
      try {
        const authStore = useAuthStore();

        if (authStore.user?.name) {
          if (this.modelOwner == '') {
            this.modelOwner = authStore.user.name;
          }
          if (this.modelPOC == '') {
            this.modelPOC = authStore.user.name;
          }
        }
        const cardPackage = {
          title: this.modelName,
          task: this.modelTask,
          tags: this.tags,
          frameworks: this.frameworks,
          owner: this.modelOwner,
          pointOfContact: this.modelPOC,
          markdown: this.markdownContent,
          performance: this.performanceMarkdown,
          artifacts: [
            {
              name: 'model',
              artifactType: 'model',
              url: this.modelPath,
            },
          ],
          description: this.modelDesc,
          explanation: this.modelExplain,
          usage: this.modelUsage,
          limitations: this.modelLimitations,
        } as ModelCard;

        if (this.experimentID != '' && this.experimentPlatform != '') {
          cardPackage.experiment = {
            connector: this.experimentPlatform,
            experimentId: this.experimentID,
          };
        }

        if (this.datasetID != '' && this.datasetPlatform != '') {
          cardPackage.dataset = {
            connector: this.datasetPlatform,
            datasetId: this.datasetID,
          };
        }
        // Create Inference Service
        const inferenceServiceStore = useInferenceServiceStore();
        const { serviceName } = await inferenceServiceStore.createService(
          this.modelName,
          this.imageUri,
          this.containerPort,
          this.uniqueEnv
        );
        cardPackage.inferenceServiceName = serviceName;
        // Submit Model
        const modelStore = useModelStore();
        const { modelId, creatorUserId } = await modelStore.createModel(
          cardPackage
        );
        Notify.create({
          message: 'Successfully created model',
          icon: 'success',
          color: 'secondary',
        });
        return { modelId, creatorUserId };
      } catch (error) {
        Notify.create({
          message: 'Failed to create model',
          icon: 'warning',
          color: 'error',
        });
      }
    },
    async createModelWithVideo() {
      try {
        const authStore = useAuthStore();
        const uploadStore = useUploadStore();
        const videoUploader = uploadStore.uploadVideo(this.exampleVideo);
        let videoLocation = '';
        videoUploader.then((data) => {
          videoLocation = data;
        });
        if (authStore.user?.name) {
          if (this.modelOwner == '') {
            this.modelOwner = authStore.user.name;
          }
          if (this.modelPOC == '') {
            this.modelPOC = authStore.user.name;
          }
        }
        const cardPackage = {
          title: this.modelName,
          task: this.modelTask,
          videoLocation: videoLocation,
          tags: this.tags,
          frameworks: this.frameworks,
          owner: this.modelOwner,
          pointOfContact: this.modelPOC,
          markdown: this.markdownContent,
          performance: this.performanceMarkdown,
          artifacts: [
            {
              name: 'model',
              artifactType: 'model',
              url: this.modelPath,
            },
          ],
          description: this.modelDesc,
          explanation: this.modelExplain,
          usage: this.modelUsage,
          limitations: this.modelLimitations,
        } as ModelCardNoInference;

        if (this.experimentID != '' && this.experimentPlatform != '') {
          cardPackage.experiment = {
            connector: this.experimentPlatform,
            experimentId: this.experimentID,
          };
        }

        if (this.datasetID != '' && this.datasetPlatform != '') {
          cardPackage.dataset = {
            connector: this.datasetPlatform,
            datasetId: this.datasetID,
          };
        }
        const modelStore = useModelStore();
        const { modelId, creatorUserId } = await modelStore.createModelVideo(
          cardPackage
        );
        Notify.create({
          message: 'Successfully created model',
          type: 'positive',
        });
        return { modelId, creatorUserId };
      } catch (error) {
        Notify.create({
          message: 'Failed to create model',
          type: 'negative',
        });
      }
    },
  },
  persist: {
    storage: localStorage,
    paths: [
      'step',
      'tags',
      'frameworks',
      'modelPath',
      'experimentPlatform',
      'experimentID',
      'datasetPlatform',
      'datasetID',
      'modelName',
      'modelTask',
      'modelOwner',
      'modelPOC',
      'modelDesc',
      'modelExplain',
      'modelUsage',
      'modelLimitations',
      'markdownContent',
      'inferenceImage',
      'performanceMarkdown',
      'imageUri',
      'containerPort',
      'serviceName',
      'previewServiceName',
      'previewServiceUrl',
      'env',
    ],
  },
});
