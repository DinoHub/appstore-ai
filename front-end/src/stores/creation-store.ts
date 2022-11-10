import { AxiosError } from 'axios';
import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import { Cookies } from 'quasar';

export const useCreationStore = defineStore('creationStore', {
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
      inferenceImage: '' as string,
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
    };
  },
  getters: {},
  actions: {
    async launchImage(inferenceImage: string, userId: string): Promise<void> {
      try {
        console.log(inferenceImage);
        console.log(userId);
        const pushedApp = await api.post(
          '/engines/',
          {
            owner_id: userId,
            image_uri: inferenceImage,
            service_name: inferenceImage + '123123',
          },
          {
            headers: {
              'Content-Type': 'application/json',
              Accept: 'application/json',
            },
          }
        );
      } catch {
        console.log('failure');
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
    ],
  },
});
