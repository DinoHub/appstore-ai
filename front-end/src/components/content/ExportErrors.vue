<template>
  <q-card style="max-height: 80vh">
    <q-splitter v-model="splitterModel" style="height: 80vh">
      <template v-slot:before>
        <q-tabs v-model="tab" vertical class="text-primary">
          <q-tab name="card" icon="credit_card" label="Card Metadata" />
          <q-tab name="service" icon="build" label="Service Metadata" />
          <q-tab
            name="model_file"
            icon="precision_manufacturing"
            label="Model File"
          />
          <q-tab
            name="example_video"
            icon="ondemand_video"
            label="Example Video"
          />
          <q-tab name="unexpected" icon="error" label="Unexpected"></q-tab>
        </q-tabs>
      </template>

      <template v-slot:after>
        <q-tab-panels
          v-model="tab"
          animated
          vertical
          transition-prev="jump-up"
          transition-next="jump-up"
        >
          <q-tab-panel name="intro">
            <div class="text-h6 q-mb-sm">Legend of Errors</div>

            <p>
              This is the legend that contains all possible errors that the
              export process can encounter.
            </p>
            <p>
              It will serve as an aid for you, detailing all errors that the
              export process can encounter, the possible reasons why each error
              occurs and possible solutions to try to resolve them.
            </p>
            <p>
              Utilise the tabs panel on the left to view the different errors.
            </p>

            <div class="text-h6 q-mb-sm">IMPORTANT</div>
            <p>
              The exporter itself does not encapsulate the full exporting
              process as it is unable to download any Docker images such as the
              inference service's Docker image.
            </p>
            <p>
              This is one part that has to be done manually, so ensure that you
              look through the JSON files that constitute the card and service
              metadata to download any required Docker images.
            </p>
          </q-tab-panel>
          <q-tab-panel name="card">
            <div class="text-h6 q-mb-sm">
              Card metadata could not be retrieved
            </div>
            <p>
              This error dictates that the model card's data was not added to
              the export package.
            </p>
            <p>Possible reasons why this might happen:</p>
            <ul class="q-pl-lg">
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend failed to get the card metadata from the database<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to the backend being unable to connect to the
                database because of incorrect name, IP address or credentials,
                etc.<br />
                <strong><u>Solution</u></strong
                ><br />
                Ensure that the variables used to connect to the database are
                valid and modify the configuration accordingly if incorrect
              </li>
              <br />
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend failed to convert the retrieved card to a JSON
                format<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to a mismatched version of the data if the
                data stored was older and the app store was updated with new
                card schema<br />
                <strong><u>Solution</u></strong
                ><br />
                Check the database entry for a mismatch in data version if it
                exists and update the entry to the appropriate schema if
                applicable
              </li>
              <br />
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend was unable to upload the card data to the S3
                bucket<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to the backend being unable to connect to the
                S3 bucket due to invalid credentials or address<br />
                <strong><u>Solution</u></strong
                ><br />
                Ensure that the variables used to connect to the S3 bucket are
                valid and modify the configuration accordingly if incorrect
              </li>
            </ul>

            <p>For additional information please check the backend's logs.</p>
          </q-tab-panel>

          <q-tab-panel name="service">
            <div class="text-h6 q-mb-sm">
              Service metadata could not be retrieved
            </div>
            <p>
              This error dictates that the inference services's data was not
              added to the export package.
            </p>
            <p>Possible reasons why this might happen:</p>
            <ul class="q-pl-lg">
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend failed to get the service metadata from the
                database<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to the backend being unable to connect to the
                database because of incorrect name, IP address or credentials,
                etc.<br />
                <strong><u>Solution</u></strong
                ><br />
                Ensure that the variables used to connect to the database are
                valid and modify the configuration accordingly if incorrect
              </li>
              <br />
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend failed to convert the retrieved service data to a
                JSON format<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to a mismatched version of the data if the
                data stored was older and the app store was updated with new
                inference service schema<br />
                <strong><u>Solution</u></strong
                ><br />
                Check the database entry for a mismatch in data version if it
                exists and update the entry to the appropriate schema if
                applicable
              </li>
              <br />
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend was unable to upload the service data to the S3
                bucket<br />
                <strong><u>Reason</u></strong
                ><br />
                This is likely due to the backend being unable to connect to the
                S3 bucket due to invalid credentials or address<br />
                <strong><u>Solution</u></strong
                ><br />
                Ensure that the variables used to connect to the S3 bucket are
                valid and modify the configuration accordingly if incorrect
              </li>
            </ul>
            <p>For additional information please check the backend's logs.</p>
          </q-tab-panel>

          <q-tab-panel name="model_file">
            <div class="text-h6 q-mb-sm">Model file could not be retrieved</div>
            <p>
              This error dictates that the model file provided for the model
              card was not added to the export package.
            </p>
            <p>Possible reasons why this might happen:</p>
            <ul class="q-pl-lg">
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend could not connect to the relevant S3 bucket of the
                model file to retrieve it<br />
                <strong><u>Reasons</u></strong
                ><br />
                <ol type="1" class="q-pl-md">
                  <li>
                    The backend being unable to connect to the S3 bucket that
                    the model file is stored in due to invalid/insufficient
                    credentials
                  </li>
                  <li>
                    The URL provided for the model file is invalid and is
                    incorrect
                  </li>
                </ol>
                <strong><u>Solutions</u></strong
                ><br />
                <ol type="1" class="q-pl-md">
                  <li>
                    Ensure that the variables used to connect to the S3 bucket
                    are valid/sufficient and modify the configuration
                    accordingly if incorrect
                  </li>
                  <li>
                    Seek the creator/maintainer of the model to get the correct
                    model file URL
                  </li>
                </ol>
              </li>
            </ul>
            <p>For additional information please check the backend's logs.</p>
          </q-tab-panel>

          <q-tab-panel name="example_video">
            <div class="text-h6 q-mb-sm">
              Example video could not be retrieved
            </div>
            <p>
              This error dictates that the example video provided to showcase
              the model's performance was not added to the export package.
            </p>
            <p>Possible reasons why this might happen:</p>
            <ul class="q-pl-lg">
              <li>
                <strong><u>Problem</u></strong
                ><br />
                The backend failed to retrieve the example video related to the
                model stored in the S3 bucket<br />
                <strong><u>Reason</u></strong
                ><br />
                The backend being unable to connect to the S3 bucket that the
                model file is stored in due to invalid/insufficient
                credentials<br />
                <strong><u>Solution</u></strong
                ><br />
                Ensure that the variables used to connect to the S3 bucket are
                valid/sufficient and modify the configuration accordingly if
                incorrect
              </li>
            </ul>
            <p>For additional information please check the backend's logs.</p>
          </q-tab-panel>

          <q-tab-panel name="unexpected">
            <div class="text-h6 q-mb-sm">Unexpected error occurred</div>
            <p>
              This dictates a catastrophic error has happened during the export
              process that was unexpected by the exporting system.
            </p>
            <p>
              Check the backend of the AI Appstore to identify the problem that
              will be present in the logs as this is likely a code error that
              has occurred or something completely unaccounted for.
            </p>
          </q-tab-panel>
        </q-tab-panels>
      </template>
    </q-splitter>
  </q-card>
</template>
<script>
import { ref } from 'vue';

export default {
  setup() {
    return {
      tab: ref('intro'),
      splitterModel: 27.0,
    };
  },
};
</script>
