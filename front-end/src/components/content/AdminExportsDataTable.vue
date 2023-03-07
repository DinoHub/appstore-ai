<template>
  <div class="row">
    <q-drawer show-if-above :model-value="props.filterDrawer" class="">
      <aside class="col-4 q-pt-md">
        <q-form>
          <div class="text-h6 q-pl-md">Query Filters</div>
          <q-expansion-item
            default-opened
            icon="date_range"
            label="Time Initiated"
          >
            <q-date
              v-model="exportStore.timeInitiatedRange"
              range
              minimal
              color="primary"
              class="q-mt-sm q-ml-sm q-mb-sm"
            />
          </q-expansion-item>
          <q-expansion-item icon="today" label="Time Completed">
            <q-date
              v-model="exportStore.timeCompletedRange"
              range
              minimal
              color="primary"
              class="q-mt-sm q-ml-sm"
          /></q-expansion-item>
        </q-form>
      </aside>
    </q-drawer>
  </div>
  <div class="row justify-center">
    <q-table
      class="col-11 q-ml-md"
      ref="tableRef"
      rows-per-page-label="Exports per page:"
      :rows-per-page-options="[5, 7, 10, 15, 20, 25, 50]"
      :rows="rows"
      :columns="columns"
      :filter="exportStore"
      :loading="loading"
      row-key="timeInitiated"
      v-model:pagination="pagination"
      v-model:selected="selected"
      selection="multiple"
      @request="onSearchRequest"
    >
      <template v-slot:top>
        <q-btn
          class="q-ml-sm"
          color="negative"
          v-if="selected.length > 0"
          :label="`Remove (${selected.length})`"
          @click="styleRemoval"
        />

        <q-space />
        <form autocomplete="off" class="q-mr-md" style="width: 22.5%">
          <q-input
            hint="Search By ID"
            dense
            debounce="700"
            color="primary"
            v-model="exportStore.idSearch"
            label=""
            type="search"
          >
            <template v-if="exportStore.idSearch" v-slot:append>
              <q-icon
                name="close"
                @click.stop.prevent="exportStore.idSearch = ''"
              />
            </template>
            <template v-slot:before>
              <q-icon name="search" />
            </template>
          </q-input>
        </form>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-checkbox v-model="props.selected" color="grey-8" />
          </q-td>
          <q-td key="userId" :props="props">
            {{ props.row.userId }}
          </q-td>
          <q-td key="status" :props="props">
            <q-badge
              :class="
                props.row.status == 'Completed' ? 'bg-positive' : 'bg-secondary'
              "
              >{{ props.row.status }}</q-badge
            >
          </q-td>
          <q-td key="timeInitiated" :props="props">{{
            `${new Date(props.row.timeInitiated).getDate()}/${
              new Date(props.row.timeInitiated).getMonth() + 1
            }/${new Date(props.row.timeInitiated).getFullYear()}, ${new Date(
              props.row.timeInitiated
            ).toLocaleTimeString()}`
          }}</q-td>
          <q-td key="timeCompleted" :props="props"
            ><div v-if="props.row.timeCompleted != null">
              {{
                `${new Date(props.row.timeCompleted).getDate()}/${
                  new Date(props.row.timeCompleted).getMonth() + 1
                }/${new Date(
                  props.row.timeCompleted
                ).getFullYear()}, ${new Date(
                  props.row.timeCompleted
                ).toLocaleTimeString()}`
              }}
            </div></q-td
          >
          <q-td key="models" :props="props"
            ><q-btn
              size="sm"
              color="secondary"
              round
              dense
              @click="props.expand = !props.expand"
              :icon="props.expand ? 'remove' : 'add'"
            />
          </q-td>
          <q-td key="exportLocation" :props="props">{{
            props.row.exportLocation
          }}</q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <q-table hide-bottom :rows="props.row.models" :columns="subColumns">
              <template v-slot:body-cell-progress="props">
                <q-td class="q-gutter-xs" :props="props">
                  <q-badge
                    v-if="props.value != null"
                    :class="
                      props.value == 'Failed' ? 'bg-negative' : 'bg-positive'
                    "
                    >{{ props.value }}</q-badge
                  >
                  <q-badge v-if="props.value == null" :class="'bg-secondary'"
                    >In Progress</q-badge
                  >
                </q-td>
              </template>
              <template v-slot:body-cell-reason="props">
                <q-td :props="props" v-if="props.value != ''">
                  <div v-for="x in props.value.split(', ')" :key="x">
                    <q-chip
                      icon="warning"  
                      square
                      dense
                      color="warning"
                      text-color="black"
                      >{{ x }}</q-chip
                    >
                  </div>
                </q-td>
                <q-td :props="props" v-if="props.value == ''"></q-td>
              </template>
            </q-table>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>

  <q-dialog v-model="removePopup" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Delete Export Logs</div>
        <q-list>
          <q-item-label header class="text-black text-bold q-pl-none"
            >Deleting {{ selected.length }} exports(s):</q-item-label
          ><q-item
            v-for="x in selected"
            :key="x.userId"
            class="q-pl-none q-pt-none"
          >
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" icon="get_app" />
            </q-item-section>

            <q-item-section>
              {{ x.userId }}
              {{
                ` (${new Date(x.timeInitiated).getDate()}/${
                  new Date(x.timeInitiated).getMonth() + 1
                }/${new Date(x.timeInitiated).getFullYear()}, ${new Date(
                  x.timeInitiated
                ).toLocaleTimeString()})`
              }}
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          rounded
          outline
          label="Cancel"
          padding="sm md"
          color="error"
          v-close-popup
        />
        <q-space />
        <q-btn
          rounded
          label="Confirm"
          color="primary"
          padding="sm md"
          outline
          v-close-popup
          @click="callDeleteExports"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { useExportsStore, Exports } from 'src/stores/exports-store';
import { onMounted, Ref, ref } from 'vue';
import { Notify, QTable, QTableColumn, QTableProps } from 'quasar';
import { Pagination, ExportsSearchFilter } from './models';

export interface ExportsDataTableProps {
  rows?: Exports[];
  showFilter?: boolean;
  filterDrawer?: boolean;
  filter: ExportsSearchFilter;
  pagination: Pagination;
}

const selected = ref([]);
const removePopup = ref(false);

// Stores & Props
const exportStore = useExportsStore();
const props = defineProps<ExportsDataTableProps>();
const pagination: Ref<Pagination> = ref(props.pagination);
pagination.value.rowsPerPage = 10;

// Data Table
const tableRef: Ref<QTable | undefined> = ref();
const rows: Ref<Exports[]> = ref([]); // store data in table
const loading = ref(false);

function callDeleteExports() {
  exportStore
    .removeExports(selected.value)
    .then(() => {
      selected.value = [];
      tableRef.value?.requestServerInteraction();
    })
    .catch((err) => {
      Notify.create({
        message: 'Failed to delete exports',
        type: 'negative',
      });
      console.error(err);
    });
}

function styleRemoval() {
  removePopup.value = true;
}

// set up columns for the table
const columns: QTableColumn[] = [
  {
    name: 'userId',
    required: true,
    label: 'ID',
    align: 'left',
    field: 'userId',
    sortable: true,
  },
  {
    name: 'status',
    required: false,
    label: 'Status',
    field: 'status',
    sortable: false,
    align: 'right',
  },
  {
    name: 'timeInitiated',
    required: true,
    label: 'Time Initiated',
    field: 'timeInitiated',
    format: (val) =>
      `${new Date(val).getDate()}/${new Date(val).getMonth() + 1}/${new Date(
        val
      ).getFullYear()}, ${new Date(val).toLocaleTimeString()}`,
    sortable: true,
  },
  {
    name: 'timeCompleted',
    required: true,
    label: 'Time Completed',
    field: 'timeCompleted',
    format: (val) =>
      `${new Date(val).getDate()}/${new Date(val).getMonth() + 1}/${new Date(
        val
      ).getFullYear()}, ${new Date(val).toLocaleTimeString()}`,
    sortable: true,
  },

  {
    name: 'models',
    required: false,
    label: 'Models',
    field: '',
    sortable: false,
    align: 'right',
  },
  {
    name: 'exportLocation',
    required: true,
    label: 'Export Location',
    field: 'exportLocation',
    sortable: true,
  },
];

const subColumns: QTableColumn[] = [
  {
    name: 'model_id',
    required: true,
    label: 'Model ID',
    align: 'left',
    field: 'model_id',
    sortable: true,
  },
  {
    name: 'creator_user_id',
    required: true,
    label: 'Creator ID',
    field: 'creator_user_id',
    sortable: true,
  },
  {
    name: 'progress',
    required: true,
    label: 'Status',
    field: 'progress',
  },
  {
    name: 'reason',
    required: true,
    label: 'Reason(s)',
    field: 'reason',
    align: 'left',
    format: (val) => (val != undefined ? val.join(', ') : ''),
  },
];

// search request function to get users from the backend
const onSearchRequest = (props: QTableProps) => {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy, descending } =
    props.pagination as unknown as Pagination;
  selected.value = [];
  loading.value = true;
  exportStore
    .getExportsPaginated(page, rowsPerPage, sortBy, descending)
    .then(({ results, total_rows }) => {
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total_rows;
      pagination.value.page = page ?? 1;
      pagination.value.sortBy = sortBy;
      pagination.value.descending = descending;
      pagination.value.rowsPerPage = rowsPerPage ?? 10;
      loading.value = false;
    })
    .catch((err) => {
      Notify.create({
        message: 'Failed to get exports',
        type: 'negative',
      });
      console.error(err);
    });
};

onMounted(() => {
  // TODO: overhaul this?
  // If URL contains filter params, auto add
  // Update table with latest value from Server
  tableRef.value?.requestServerInteraction();
});
</script>
