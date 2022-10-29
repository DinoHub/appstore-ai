<template>
  <div class="q-pa-md col-9" :style="vert">
    <q-stepper
      v-model="step"
      ref="stepper"
      color="primary"
      animated
      done-color="secondary"
      error-color="red"
      class="shadow-0 justify-center text-center full-height"
      header-class="no-border q-px-xl"
    >
      <q-step
        :name="1"
        title="Model & Owner Information"
        icon="person"
        :done="step > 1"
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
              :dense="dense"
              class="q-ml-md q-pb-xl"
              hint="Model Name"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <q-select
              v-model="task"
              :dense="dense"
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
              class="q-ml-md q-pr-md q-pb-xl"
              :rules="[
                (val) => val.length >= 1 || 'One or more frameworks required',
              ]"
            ></q-select>
          </div>
          <div class="col-3 q-pl-md q-ml-xl shadow-2 rounded">
            <h6 class="text-left q-mt-md q-mb-lg">Owner Information</h6>
            <q-input
              v-model="owner"
              :dense="dense"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Model Owner (Optional)"
            ></q-input>
            <q-input
              v-model="poc"
              :dense="dense"
              autogrow
              class="q-mr-md q-pb-xl"
              hint="Point of Contact (Optional)"
            ></q-input>
          </div>
        </div>
      </q-step>

      <q-step
        :name="2"
        title="Links"
        icon="link"
        :done="step > 2"
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
              :dense="dense"
              class="q-ml-md q-pb-xl"
              hint="Model Path"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            ></q-input>
            <q-select
              v-model="exp_platform"
              :dense="dense"
              class="q-ml-md q-pb-xl"
              :options="exp_platforms"
              hint="Experiment Platform (Optional)"
            />
            <q-input
              v-if="exp_platform != ''"
              v-model="exp_id"
              :dense="dense"
              class="q-ml-md q-pb-xl"
              hint="Experiment ID"
              autogrow
              :rules="[(val) => !!val || 'Field is required']"
            >
            </q-input>
            <q-select
              v-model="dataset_platform"
              :dense="dense"
              class="q-ml-md q-pb-xl"
              :options="dataset_platforms"
              hint="Dataset Platform (Optional)"
            />
            <q-input
              v-if="dataset_platform != ''"
              v-model="dataset_id"
              :dense="dense"
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
        :name="3"
        title="Card Description"
        icon="description"
        :done="step > 3"
      >
        <div class="row justify-center">
          <div class="q-pa-md q-gutter-sm col-10 shadow-1">
            <h6 class="text-left q-mt-md q-ml-md q-mb-lg">Model Description</h6>
            <editor
              v-model="card_content"
              tinymce-script-src="https://cdn.tiny.cloud/1/v1er762uh44qnxlbr0msn2lvfsbk5wjihssryzia0va0aiov/tinymce/6/tinymce.min.js"
              api_key="v1er762uh44qnxlbr0msn2lvfsbk5wjihssryzia0va0aiov"
              :init="{
                height: 550,
                plugins:
                  'insertdatetime lists link image table help hr anchor code codesample charmap',
              }"
              toolbar="undo redo | blocks | bold italic underline 
              strikethrough | alignleft aligncenter alignright | outdent 
              indent | charmap anchor hr | bullist numlist | insertdatetime"
            />
          </div>
        </div>
      </q-step>

      <q-step
        :name="4"
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
              tinymce-script-src="https://cdn.tiny.cloud/1/v1er762uh44qnxlbr0msn2lvfsbk5wjihssryzia0va0aiov/tinymce/6/tinymce.min.js"
              api_key="v1er762uh44qnxlbr0msn2lvfsbk5wjihssryzia0va0aiov"
              :init="{
                height: 600,
                plugins:
                  'insertdatetime lists link image table help hr anchor code codesample charmap',
              }"
              toolbar="undo redo | blocks | bold italic underline 
              strikethrough | alignleft aligncenter alignright | outdent 
              indent | charmap anchor hr | bullist numlist | insertdatetime"
            />
          </div>
        </div>
      </q-step>

      <q-step :name="5" title="Inference Engine" icon="code"> </q-step>

      <template v-slot:navigation>
        <q-stepper-navigation>
          <div class="row">
            <div class="text-right col-2">
              <q-btn
                color="red"
                @click="cancel = true"
                label="Cancel"
                class="q-mr-md"
              />
            </div>
            <div class="text-right col-9">
              <q-btn
                v-if="step > 1"
                color="primary"
                @click="$refs.stepper.previous()"
                label="Back"
                class="q-mr-md"
              />
              <q-btn
                v-if="step != 5"
                @click="
                  $refs.stepper.next();
                  simulateSubmit();
                "
                color="primary"
                label="Continue"
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
</template>

<script>
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

    // variables for the tags and framework
    const tagAddUnique = ref([]);
    const frameworkAddUnique = ref([]);

    // other model and owner metadata for the 1st page of stepper
    const model_name = ref('');
    const task = ref('');
    const owner = ref('');
    const poc = ref('');

    // info about model, experiments and datasets for 2nd page of stepper
    const model_path = ref('');
    const exp_platform = ref('');
    const exp_id = ref('');
    const dataset_platform = ref('');
    const dataset_id = ref('');

    // variables for model card step 3
    const card_content = ref(`<h3>Description <a id="description"></a></h3>
                              <hr>
                              <p><span style="font-family: 'trebuchet ms', geneva, sans-serif;">The general description of your model, usually a summary paragraph that can give developers a good idea of the purpose of said model. <strong><em>(Example Text to Replace)</em></strong></span></p>
                              <p>&nbsp;</p>
                              <h3>Model Use <a id="model_use"></a></h3>
                              <hr>
                              <p>What task the model is used on, whether it's meant for downstream tasks, what genre or type of data it can be used on, etc.</p>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>You can use the raw model for masked language modeling, but it's mostly intended to be fine-tuned on a downstream task. See the model hub to look for fine-tuned versions on a task that interests you.<br><br>Note that this model is primarily aimed at being fine-tuned on tasks that use the whole sentence (potentially masked) to make decisions, such as sequence classification, token classification or question answering. For tasks such as text generation you should look at model like GPT2. <strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>
                              <p>&nbsp;</p>
                              <h3>Limitations <a id="limitations"></a></h3>
                              <hr>
                              <p>The limitation or issues that the model may possible, any biases towards certain types of data, etc.</p>
                              <p><strong>EXAMPLE:</strong></p>
                              <p>The training data used for this model contains a lot of unfiltered content from the internet, which is far from neutral. Therefore, the model can have biased predictions. <strong><em><span style="font-family: 'trebuchet ms', geneva, sans-serif;">(Example Text to Replace)</span></em></strong></p>`);

    // variables for performance metrics in model creation step 4
    const metrics_content = ref('');

    // variables for popup exits
    const cancel = ref(false);

    function simulateSubmit() {
      console.log(tagAddUnique.value);
      console.log(frameworkAddUnique.value);
      console.log(task.value);
      console.log(card_content.value);
    }
    function next() {
      $refs.stepper.previous();
    }
    return {
      step,
      simulateSubmit,
      tagAddUnique,
      frameworkAddUnique,
      task,
      model_name,
      next,
      owner,
      poc,
      cancel,
      model_path,
      exp_platform,
      exp_id,
      dataset_platform,
      dataset_id,
      tasks: [
        'Computer Vision',
        'Natural Language Processing',
        'Audio Processing',
        'Multimodal',
        'Reinforcement Learning',
        'Tabular',
      ],
      exp_platforms: ['', 'ClearML'],
      dataset_platforms: ['', 'ClearML'],
      card_content,
      metrics_content,
    };
  },
};
</script>
