<template>
  <!-- This component is similar to the ModelCardDataTable component -->
  <div class="row">
    <!-- Left sidebar -->
    <q-drawer show-if-above :model-value="props.filterDrawer">
      <aside class="col-4 q-pt-md">
        <q-form>
          <div class="text-h6 q-pl-md">Query Filters</div>
          <q-expansion-item default-opened icon="task" label="Task">
            <q-option-group
              v-model="filter.tasks"
              :options="tasks"
              color="primary"
              type="checkbox"
              class="q-pl-sm"
            ></q-option-group>
          </q-expansion-item>
          <q-expansion-item icon="code" label="Frameworks">
            <q-option-group
              v-model="filter.frameworks"
              :options="frameworks"
              color="primary"
              type="checkbox"
              class="q-pl-sm"
            ></q-option-group>
          </q-expansion-item>
          <q-expansion-item default-opened icon="tag" label="Tags">
            <q-select
              hint="Type in tags or use dropdown to add available tags"
              class="q-ma-sm q-ml-md q-mr-lg"
              color="secondary"
              v-model="filter.tags"
              use-input
              use-chips
              multiple
              autogrow
              outlined
              input-debounce="500"
              new-value-mode="add-unique"
              label="Filter by Tags"
              :options="tags"
            ></q-select>
          </q-expansion-item>
        </q-form>
      </aside>
    </q-drawer>
  </div>
  <div class="row justify-center">
    <q-table
      class="col-11 q-ml-md"
      ref="tableRef"
      :rows-per-page-options="[5, 7, 10, 15, 20, 25, 50]"
      rows-per-page-label="Models per page:"
      :rows="rows"
      :columns="columns"
      :row-key="compositeId"
      :filter="filter"
      :loading="loading"
      @request="onSearchRequest"
      v-model:selected="selected"
      selection="multiple"
      v-model:pagination="pagination"
      wrap-cells
    >
      <template v-slot:top>
        <q-btn
          class="q-ml-sm"
          color="secondary"
          v-if="selected.length == 1"
          :label="`Edit`"
          @click="editSelectedModel"
        />
        <q-btn
          class="q-ml-sm"
          color="negative"
          v-if="selected.length > 0"
          :label="`Remove (${selected.length})`"
          @click="removePopup = true"
        />
        <q-btn
          class="q-ml-sm"
          color="primary"
          v-if="selected.length > 0"
          :label="`Export (${selected.length})`"
          @click="exportPopup = true"
        />

        <q-space />
        <form autocomplete="off" class="q-mr-md" style="width: 22.5%">
          <q-input
            hint="Search By Name"
            dense
            debounce="700"
            color="primary"
            v-model="filter.title"
            label=""
            type="search"
          >
            <template v-if="filter.title" v-slot:append>
              <q-icon name="close" @click.stop.prevent="filter.title = ''" />
            </template>
            <template v-slot:before>
              <q-icon name="search" />
            </template>
          </q-input>
        </form>
        <form autocomplete="off" style="width: 22.5%">
          <q-input
            hint="Search By Creator ID"
            dense
            label=""
            debounce="700"
            color="primary"
            v-model="filter.creatorUserIdPartial"
            type="search"
          >
            <template v-if="filter.creatorUserIdPartial" v-slot:append>
              <q-icon
                name="close"
                @click.stop.prevent="filter.creatorUserIdPartial = ''"
              />
            </template>
            <template v-slot:before>
              <q-icon name="search" />
            </template>
          </q-input>
        </form>
      </template>

      <template v-slot:body-cell-tags="props">
        <q-td class="q-gutter-xs" :props="props">
          <q-badge
            color="secondary"
            dense
            rounded
            v-for="x in props.value.split(', ')"
            :key="x"
            :label="x"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-frameworks="props">
        <q-td class="q-gutter-xs" :props="props">
          <q-badge
            color="tertiary"
            dense
            rounded
            v-for="x in props.value.split(', ')"
            :key="x"
            :label="x"
          />
        </q-td>
      </template>
    </q-table>
  </div>

  <q-dialog v-model="removePopup" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Remove Models</div>
        <q-list>
          <q-item-label header class="text-black text-bold q-pl-none"
            >Deleting {{ selected.length }} models(s):</q-item-label
          ><q-item
            v-for="x in selected"
            :key="x.creatorUserId"
            class="q-pl-none q-pt-none"
          >
            <q-item-section avatar>
              <q-avatar
                color="primary"
                text-color="white"
                icon="tablet_android"
              />
            </q-item-section>

            <q-item-section>
              {{ x.title }} {{ ` (${x.creatorUserId})` }}
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          rounded
          no-caps
          outline
          label="Cancel"
          padding="sm md"
          color="error"
          v-close-popup
        />
        <q-space></q-space>
        <q-btn
          rounded
          no-caps
          label="Confirm"
          color="primary"
          padding="sm md"
          outline
          v-close-popup
          @click="deleteModels"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="exportPopup" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Export Models</div>
        <q-list>
          <q-item-label header class="text-black text-bold q-pl-none"
            >Exporting {{ selected.length }} models(s):</q-item-label
          ><q-item
            v-for="x in selected"
            :key="x.creatorUserId"
            class="q-pl-none q-pt-none"
          >
            <q-item-section avatar>
              <q-avatar
                color="primary"
                text-color="white"
                icon="tablet_android"
              />
            </q-item-section>

            <q-item-section>
              {{ x.title }} {{ ` (${x.creatorUserId})` }}
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          rounded
          no-caps
          outline
          label="Cancel"
          padding="sm md"
          color="error"
          v-close-popup
        />
        <q-space></q-space>
        <q-btn
          rounded
          no-caps
          label="Confirm"
          color="primary"
          padding="sm md"
          outline
          v-close-popup
          @click="exportModels"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { QTable, QTableColumn, QTableProps, Notify } from 'quasar';
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { onMounted, reactive, Ref, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { FormOptionValue, Pagination, SearchFilter } from './models';

export interface ModelCardDataTableProps {
  rows?: ModelCardSummary[];
  cardClass?: string;
  cardContainerClass?: string;
  showFilter?: boolean;
  filterDrawer?: boolean;
  filter: SearchFilter;
  pagination: Pagination;
}

const persistent = ref(false);
const selected = ref([]);
const exportPopup = ref(false);
const removePopup = ref(false);
const loading = ref(false);

const router = useRouter();
const route = useRoute();

// Stores & Props
const modelStore = useModelStore();
const props = defineProps<ModelCardDataTableProps>();
const pagination: Ref<Pagination> = ref(props.pagination);
pagination.value.rowsPerPage = 10;

const tasks: FormOptionValue[] = reactive([]);
const frameworks: FormOptionValue[] = reactive([]);
const tags: string[] = reactive([]);

if (props.showFilter) {
  // Dynamically get filter options
  modelStore
    .getFilterOptions()
    .then((data) => {
      tags.splice(0, tags.length, ...data.tags);
      frameworks.splice(
        0,
        frameworks.length,
        ...data.frameworks.map((framework: string) => {
          return {
            label: framework,
            value: framework,
          };
        })
      );
      tasks.splice(
        0,
        tasks.length,
        ...data.tasks.map((task: string) => {
          return {
            label: task,
            value: task,
          };
        })
      );
    })
    .catch(() => {
      console.error('Failed to get filter options');
      Notify.create({
        message: 'Failed to retrieve filter options from database',
        color: 'negative',
      });
    });
}

// Data Table
const tableRef: Ref<QTable | undefined> = ref();
const rows: Ref<ModelCardSummary[]> = ref([]); // store data in table

const filter: SearchFilter = reactive(props.filter);

const compositeId = (row: ModelCardSummary) =>
  `${row.creatorUserId}/${row.modelId}`;

const columns: QTableColumn[] = [
  {
    name: 'title',
    required: true,
    label: 'Name',
    field: 'title',
    align: 'left',
    sortable: true,
  },
  {
    name: 'modelId',
    required: true,
    label: 'Model ID',
    field: 'modelId',
    align: 'left',
    sortable: true,
  },
  {
    name: 'creatorUserIdPartial',
    required: true,
    label: 'Creator ID',
    field: 'creatorUserId',
    sortable: true,
  },
  {
    name: 'task',
    required: false,
    label: 'Task',
    field: 'task',
    sortable: true,
  },

  {
    name: 'tags',
    required: true,
    label: 'Tags',
    field: 'tags',
    format: (val) => val.join(', '),
  },
  {
    name: 'frameworks',
    required: true,
    label: 'Frameworks',
    field: 'frameworks',
    format: (val) => val.join(', '),
  },
  {
    name: 'created',
    required: true,
    label: 'Date Created',
    field: 'created',
    format: (val) =>
      `${new Date(val).getDate()}/${new Date(val).getMonth() + 1}/${new Date(
        val
      ).getFullYear()}, ${new Date(val).toLocaleTimeString()}`,
    sortable: true,
  },
  {
    name: 'lastModified',
    required: true,
    label: 'Last Modified',
    field: 'lastModified',
    format: (val) =>
      `${new Date(val).getDate()}/${new Date(val).getMonth() + 1}/${new Date(
        val
      ).getFullYear()}, ${new Date(val).toLocaleTimeString()}`,
    sortable: true,
  },
];

const onSearchRequest = (props: QTableProps) => {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy, descending } =
    props.pagination as unknown as Pagination;

  loading.value = true;
  modelStore
    .getModels({
      p: page,
      n: rowsPerPage,
      sort: sortBy ?? '_id',
      desc: descending ?? false,
      all: rowsPerPage === 0,
      ...filter,
    })
    .then(({ results, total }) => {
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total;
      pagination.value.page = page ?? 1;
      pagination.value.rowsPerPage = rowsPerPage ?? 0;
      pagination.value.sortBy = sortBy;
      pagination.value.descending = descending;
      loading.value = false;
    })
    .catch((err) => {
      console.error(err);
      Notify.create({
        message: 'Failed to retrieve models from database',
        color: 'negative',
      });
      loading.value = false;
    });
};

const exportModels = () => {
  modelStore
    .exportModels(selected.value)
    .then(() => {
      Notify.create({
        message: 'Export request successfully initiated!',
        type: 'positive',
      });
      tableRef.value?.requestServerInteraction();
      selected.value = [];
    })
    .catch(() => {
      Notify.create({
        message: 'Export request failed...',
        type: 'negative',
      });
    });
};

const deleteModels = () => {
  modelStore.deleteModelMultiple(selected.value).then(() => {
    tableRef.value?.requestServerInteraction();
    selected.value = [];
  });
};

const editSelectedModel = () => {
  router.push(
    `/admin/models/${selected.value[0].creatorUserId}/${selected.value[0].modelId}/edit/metadata`
  );
};

onMounted(() => {
  // TODO: overhaul this?
  // If URL contains filter params, auto add
  if (props.showFilter) {
    const params = route.query;
    // Process tags
    if (params.tags) {
      if (!filter.tags) {
        filter.tags = [];
      }
      if (typeof params.tags === 'string') {
        filter.tags.push(params.tags);
      } else {
        filter.tags = params.tags;
      }
    }
    if (params.frameworks) {
      if (!filter.frameworks) {
        filter.frameworks = [];
      }
      if (typeof params.frameworks === 'string') {
        filter.frameworks.push(params.frameworks);
      } else {
        filter.frameworks = params.frameworks;
      }
    }
    if (params.tasks) {
      if (!filter.tasks) {
        filter.tasks = [];
      }
      if (typeof params.tasks === 'string') {
        filter.tasks.push(params.tasks);
      } else {
        filter.tasks = params.tasks;
      }
    }
    router.replace({ query: undefined });
  }
  // Update table with latest value from Server
  tableRef.value?.requestServerInteraction();
});
</script>
