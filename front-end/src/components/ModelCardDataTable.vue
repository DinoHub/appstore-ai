<template>
  <div class="row">
    <aside class="col col-sm-3" v-if="showFilter">
      <q-form>
        <div class="text-h6">Query Filters</div>
        <q-expansion-item default-opened label="Task">
          <q-option-group
            v-model="filter.tasks"
            :options="tasks"
            color="primary"
            type="checkbox"
          ></q-option-group>
        </q-expansion-item>
        <q-expansion-item label="Frameworks">
          <q-option-group
            v-model="filter.frameworks"
            :options="frameworks"
            color="primary"
            type="checkbox"
          ></q-option-group>
        </q-expansion-item>
        <q-expansion-item default-opened label="Tags">
          <q-select
            hint="Type in tags or use dropdown to add available tags"
            v-model="filter.tags"
            use-input
            use-chips
            multiple
            autogrow
            input-debounce="0"
            new-value-mode="add-unique"
            :options="tags"
          ></q-select>
        </q-expansion-item>
      </q-form>
    </aside>
    <main class="col">
      <q-table
        ref="tableRef"
        grid
        :rows="rows"
        :columns="columns"
        :row-key="compositeId"
        v-model:pagination="pagination"
        :filter="filter"
        :loading="loading"
        @request="onSearchRequest"
        binary-state-sort
      >
        <template v-slot:top-left>
          <slot name="top-left"></slot>
        </template>
        <template v-slot:top-right>
          <q-select
            label="Sort by"
            v-model="pagination.sortBy"
            :options="sortOptions"
            emit-value
            map-options
            @update:model-value="tableRef.requestServerInteraction()"
          >
          </q-select>
          <q-input
            borderless
            dense
            debounce="300"
            v-model="filter.title"
            placeholder="Search"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </template>
        <template v-slot:item="props">
          <model-card
            class="q-ma-md"
            :card-class="cardClass"
            :title="props.row.title"
            :model-id="props.row.modelId"
            :creator-user-id="props.row.creatorUserId"
            :tags="props.row.tags"
            :frameworks="props.row.frameworks"
            :summary="props.row.summary"
          ></model-card>
        </template>
      </q-table>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { onMounted, reactive, Ref, ref } from 'vue';
import { useRoute } from 'vue-router';
import ModelCard from './ModelCard.vue';
import { FormOptionValue, Pagination, SearchFilter } from './models';

export interface Props {
  rows?: ModelCardSummary[];
  cardClass?: string;
  showFilter?: boolean;
  filter: SearchFilter;
}

const props = defineProps<Props>();

const tableRef = ref();
const filter: SearchFilter = reactive(props.filter);
const loading = ref(false);

const modelStore = useModelStore();

const pagination: Ref<Pagination> = ref({
  sortBy: '_id',
  descending: false,
  page: 1,
  rowsPerPage: 3,
  rowsNumber: 1,
});

const rows: Ref<ModelCardSummary[]> = ref([]);

const sortOptions = Object.freeze([
  {
    label: 'ID',
    value: '_id',
  },
  {
    label: 'Title',
    value: 'title',
  },
  {
    label: 'Last Updated',
    value: 'lastUpdated',
  },
]);

const tasks = reactive(
  modelStore.tasks.map((task: string) => {
    return {
      label: task,
      value: task,
    };
  }),
);
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
        }),
      );
      tasks.splice(
        0,
        tasks.length,
        ...data.tasks.map((task: string) => {
          return {
            label: task,
            value: task,
          };
        }),
      );
    })
    .catch(() => {
      console.error('Failed to get filter options');
    });
}

const columns = [
  {
    name: 'title',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'title',
  },
  {
    name: 'creatorUserId',
    required: true,
    label: 'Creator',
    field: 'creatorUserId',
  },
  {
    name: 'modelId',
    required: true,
  },
  {
    name: 'description',
    required: true,
    label: 'Description',
    field: 'description',
  },
  {
    name: 'tags',
    required: true,
    label: 'Tags',
    field: 'tags',
  },
  {
    name: 'summary',
    required: false,
    label: 'Summary',
    field: 'summary',
  },
];

function compositeId(row: ModelCardSummary): string {
  return `${row.creatorUserId}/${row.modelId}`;
}

function onSearchRequest(props: any) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination;
  loading.value = true;
  modelStore
    .getModels({
      p: page,
      n: rowsPerPage,
      sort: sortBy,
      desc: descending,
      all: rowsPerPage === 0,
      ...filter,
    })
    .then(({ results, total }) => {
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total;
      pagination.value.page = page;
      pagination.value.rowsPerPage = rowsPerPage;
      pagination.value.sortBy = sortBy;
      pagination.value.descending = descending;
      loading.value = false;
    });
}

onMounted(() => {
  tableRef.value.requestServerInteraction();
});
</script>
