<template>
  <div class="q-pa-md col-9">
    <q-stepper
      v-model="step"
      ref="stepper"
      animated
      done-color="secondary"
      error-color="red"
      color="primary"
      class="shadow-0 justify-center text-center full-height"
      header-class="no-border q-px-xl"
    >
      <q-step
        :name="1"
        title="Links"
        icon="link"
        :done="
          model_path != '' &&
          (exp_id != '' || exp_platform == '') &&
          (dataset_id != '' || dataset_platform == '')
        "
        :error="
          model_path == '' ||
          (exp_id == '' && exp_platform != '') ||
          (dataset_id == '' && dataset_platform != '')
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-4 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Links</h6>
            <q-input
              v-model="model_path"
              class="q-ml-md q-pb-xl"
              hint="Model Path"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <q-select
              v-model="exp_platform"
              class="q-ml-md q-pb-xl"
              :options="exp_platforms"
              hint="Experiment Platform (Optional)"
            />
            <q-input
              v-if="exp_platform != ''"
              v-model="exp_id"
              class="q-ml-md q-pb-xl"
              hint="Experiment ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
            <q-select
              v-model="dataset_platform"
              class="q-ml-md q-pb-xl"
              :options="dataset_platforms"
              hint="Dataset Platform (Optional)"
            />
            <q-input
              v-if="dataset_platform != ''"
              v-model="dataset_id"
              class="q-ml-md q-pb-xl"
              hint="Dataset ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="2"
        title="Model & Owner Information"
        icon="person"
        :done="
          task != '' &&
          model_name != '' &&
          tagAddUnique.length > 0 &&
          frameworkAddUnique.length > 0
        "
        :error="
          task == '' ||
          model_name == '' ||
          tagAddUnique.length <= 0 ||
          frameworkAddUnique.length <= 0
        "
      >
        <div class="row justify-center full-height" style="min-height: 35rem">
          <div class="col-3 q-pr-md q-mr-xl shadow-2 rounde">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Information</h6>
            <q-input
              v-model="model_name"
              class="q-ml-md q-pb-xl"
              hint="Model Name"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
              reactive-rules
            ></q-input>
            <q-select
              v-model="task"
              class="q-ml-md q-pb-xl"
              :options="tasks"
              hint="Task"
              :rules="[(val) => !!val || 'Field is required']"
            />
          </div>
          <div class="col-3 q-mx-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Tags</h6>
            <q-select
              hint="Tags"
              v-model="tagAddUnique"
              use-input
              use-chips
              multiple
              autogrow
              hide-dropdown-icon
              input-debounce="0"
              new-value-mode="add-unique"
              :loading="loading_exp"
              class="q-ml-md q-pr-md q-pb-xl"
              :rules="[(val) => val.length >= 1 || 'One or more tags required']"
            />
            <q-select
              hint="Frameworks"
              v-model="frameworkAddUnique"
              use-input
              use-chips
              multiple
              autogrow
              hide-dropdown-icon
              input-debounce="0"
              new-value-mode="add-unique"
              :loading="loading_exp"
              class="q-ml-md q-pr-md q-pb-xl"
              :rules="[
                (val) => val.length >= 1 || 'One or more frameworks required',
              ]"
            />
          </div>
          <div class="col-3 q-pl-md q-ml-xl shadow-2 rounded">
            <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
            <q-input
              v-model="owner"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Model Owner (Optional)"
            ></q-input>
            <q-input
              v-model="poc"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Point of Contact (Optional)"
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="3"
        title="Model Description"
        icon="person"
        :done="task != ''"
        :error="task == ''"
      >
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Description</h6>
            <q-input
              v-model="model_desc"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Explanation</h6>
            <q-input
              v-model="model_explain"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md q-mb-lg shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Usage</h6>
            <q-input
              v-model="model_use"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
            ></q-input>
          </div>
        </div>
        <div class="row justify-center full-height" style="min-height: 9rem">
          <div class="col-9 q-pr-md shadow-2 rounded">
            <h6 class="text-left q-mt-md q-ml-md q-mb-sm">Model Limitations</h6>
            <q-input
              v-model="model_limit"
              class="q-ml-md q-mb-lg"
              type="textarea"
              filled
            ></q-input>
          </div>
        </div>
      </q-step>
      <q-step
        :name="4"
        title="Card Markdown"
        icon="assignment"
        :done="card_content.includes('(Example Text to Replace)') == false"
        :error="card_content.includes('(Example Text to Replace)') != false"
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-ml-md q-mb-sm">Card Markdown</h6>
            <p class="text-left q-ml-md q-mb-sm">
              This is the HTML markdown that will shown in the model page.<br />
              Style it to your liking and display whatever additional
              information you would like, such as tables, lists, code samples or
              images. <br />
              You can follow the example content structure or come up with
              something else.
            </p>
            <div
              class="text-left q-ml-md q-mb-md text-italic text-negative"
              v-if="card_content.includes('(Example Text to Replace)') != false"
            >
              <q-icon class="" name="error" size="1.5rem" />
              Please remove the example content and style your own content
            </div>
            <editor
              v-model="card_content"
              :init="{
                height: 650,
                plugins:
                  'insertdatetime lists link image table help anchor code codesample charmap advlist',
              }"
              :toolbar="desc_toolbar"
            />
          </div>
        </div>
      </q-step>

      <q-step
        :name="5"
        title="Performance Metrics"
        icon="leaderboard"
        :done="step > 4"
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">
              Performance Metrics
            </h6>
            <editor
              v-model="metrics_content"
              :init="{
                height: 600,
                plugins:
                  'insertdatetime lists link image table help anchor code codesample charmap',
              }"
              toolbar="undo redo | blocks | bold italic underline 
              strikethrough | alignleft aligncenter alignright | outdent 
              indent | charmap anchor hr | bullist numlist | insertdatetime graphTinymcePlugin"
            />
          </div>
        </div>
      </q-step>

      <q-step :name="6" title="Inference Engine" icon="code"> </q-step>

      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row">
            <div class="text-right col-2">
              <q-btn
                color="red"
                @click="cancel = true"
                label="Cancel"
                class="q-mr-md"
                :disable="button_disable"
              />
            </div>
            <div class="text-right col-9">
              <q-btn
                v-if="step > 1"
                color="primary"
                @click="
                  $refs.stepper.previous();
                  simulateSubmit();
                "
                label="Back"
                class="q-mr-md"
                :disable="button_disable"
              />
              <q-btn
                v-if="step != 6"
                @click="
                  $refs.stepper.next();
                  simulateSubmit();
                "
                color="primary"
                label="Continue"
                :disable="button_disable"
              />
            </div>
          </div>
        </q-stepper-navigation>
      </template>
    </q-stepper>
  </div>
  <q-dialog v-model="cancel">
    <q-card>
      <q-card-section>
        <div class="text-h6">Quit</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        Are you sure you want to exit the model creation process?
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="red" v-close-popup />
        <q-space />
        <q-btn flat label="Save & Quit" color="green" v-close-popup />
        <q-btn flat label="Quit" color="primary" v-close-popup to="/" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="popupContent">
    <q-card>
      <q-card-section>
        <div class="text-h6">Markdown</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        Add Model Description text values to markdown?
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="No" color="red" v-close-popup />
        <q-btn
          flat
          label="Yes"
          color="primary"
          v-close-popup
          @click="populateEditor()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { useAuthStore } from 'src/stores/auth-store';
import { useExpStore } from 'src/stores/exp-store';
import { ref } from 'vue';
import Editor from '@tinymce/tinymce-vue';

export default {
  name: 'app',
  components: {
    editor: Editor,
  },
  setup() {
    // step for stepper to paginate
    const step = ref(1);

    // variables for lists used for the selects in model creation process
    const tasks = ref([
      'Computer Vision',
      'Natural Language Processing',
      'Audio Processing',
      'Multimodal',
      'Reinforcement Learning',
      'Tabular',
    ]);
    const exp_platforms = ref(['', 'ClearML']);
    const dataset_platforms = ref(['', 'ClearML']);

    // variables for the tags and framework
    const tagAddUnique = ref([]);
    const frameworkAddUnique = ref([]);

    // other model and owner metadata for the
    const model_name = ref('');
    const task = ref('');
    const owner = ref('');
    const poc = ref('');

    // textareas for description,usage,limitations of model
    const model_desc = ref('');
    const model_explain = ref('');
    const model_use = ref('');
    const model_limit = ref('');

    // info about model, experiments and datasets links
    const model_path = ref('');
    const exp_platform = ref('');
    const exp_id = ref('');
    const dataset_platform = ref('');
    const dataset_id = ref('');
    const loading_exp = ref(false);

    // toolbar stuff
    const desc_toolbar = [
      'undo redo | blocks | fontfamily fontsize | forecolor backcolor | bold italic underline strikethrough |',
      ' alignleft aligncenter alignright | outdent indent | bullist numlist | charmap anchor hr | insertdatetime | link image table',
    ];

    // variables for model card
    const card_content = ref(`<h3>Description <a id="description"></a></h3>
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
                              <h3>Model Use <a id="model_use"></a></h3>
                              <hr>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>What task the model is used on, whether it's meant for downstream tasks, what genre or type of data it can be used on, etc.</p>
                              <p>You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task. See the model hub to look for fine-tuned versions on a task that interests you.</p>
                              <p>Random formula: x<sup>2</sup> + &pi;</p>
                              <pre class="language-python"><code>for i in new_list:
    print(i + "hello")</code></pre>
                              <p>Note that this model is primarily aimed at being fine-tuned on tasks that use the whole sentence (potentially masked) to make decisions, such as sequence classification, token classification or question answering. For tasks such as text generation you should look at model like GPT2.&nbsp;</p><p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>
                              <p>&nbsp;</p>
                              <h3>Limitations <a id="limitations"></a></h3>
                              <hr>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>The limitation or issues that the model may possible, any biases towards certain types of data, etc.</p>
                              <blockquote>
                              <p><strong>"I think, therefore I am" -Ren&eacute; Descartes</strong></p>
                              </blockquote>
                              <p>The training data used for this model contains a lot of unfiltered content from the internet, which is far from neutral. Therefore, the model can have biased predictions.</p> <p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>`);

    // variables for performance metrics in model creation
    const metrics_content = ref('');

    // variables for popup exits
    const cancel = ref(false);
    const popupContent = ref(false);
    const button_disable = ref(false);

    // constants for stores
    const authStore = useAuthStore();
    const expStore = useExpStore();

    // function for triggering events that should happen when next step is triggered
    function simulateSubmit() {
      if (
        exp_id.value != '' &&
        step.value == 2 &&
        tagAddUnique.value.length == 0 &&
        tagAddUnique.value.length == 0
      ) {
        loading_exp.value = true;
        button_disable.value = true;
        expStore.getExperimentByID(exp_id.value).then((value) => {
          console.log(value);
          tagAddUnique.value = value.tags;
          frameworkAddUnique.value = value.frameworks;
          loading_exp.value = false;
          button_disable.value = false;
        });
      }
      if (step.value == 4) {
        popupContent.value = true;
      }
      console.log(tagAddUnique.value);
      console.log(frameworkAddUnique.value);
      console.log(step.value);
      console.log(model_desc.value);
    }
    // function for populating editor with values from previous step
    function populateEditor() {
      card_content.value = `<h3>Description <a id="description"></a></h3>
                              <hr>
                              <p>${model_desc.value}</p>
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
                              <p>${model_explain.value}</p>
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
                              <h3>Model Use <a id="model_use"></a></h3>
                              <hr>
                              <p>${model_use.value}</p>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>What task the model is used on, whether it's meant for downstream tasks, what genre or type of data it can be used on, etc.</p>
                              <p>You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task. See the model hub to look for fine-tuned versions on a task that interests you.</p>
                              <p>Random formula: x<sup>2</sup> + &pi;</p>
                              <pre class="language-python"><code>for i in new_list:
    print(i + "hello")</code></pre>
                              <p>Note that this model is primarily aimed at being fine-tuned on tasks that use the whole sentence (potentially masked) to make decisions, such as sequence classification, token classification or question answering. For tasks such as text generation you should look at model like GPT2.&nbsp;</p><p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>
                              <p>&nbsp;</p>
                              <h3>Limitations <a id="limitations"></a></h3>
                              <hr>
                              <p>${model_limit.value}</p>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>The limitation or issues that the model may possible, any biases towards certain types of data, etc.</p>
                              <blockquote>
                              <p><strong>"I think, therefore I am" -Ren&eacute; Descartes</strong></p>
                              </blockquote>
                              <p>The training data used for this model contains a lot of unfiltered content from the internet, which is far from neutral. Therefore, the model can have biased predictions.</p> <p><strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>`;
    }
    return {
      step,
      simulateSubmit,
      populateEditor,
      tagAddUnique,
      frameworkAddUnique,
      task,
      model_name,
      owner,
      poc,
      cancel,
      model_path,
      exp_platform,
      exp_id,
      dataset_platform,
      dataset_id,
      tasks,
      model_desc,
      model_explain,
      model_use,
      model_limit,
      popupContent,
      exp_platforms,
      dataset_platforms,
      card_content,
      metrics_content,
      desc_toolbar,
      loading_exp,
      button_disable,
    };
  },
};
</script>
