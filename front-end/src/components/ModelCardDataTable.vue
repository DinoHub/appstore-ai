<style>
.q-table__grid-content {
  justify-content: center;
}
</style>
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
          <div class="row items-center q-gutter-x-lg">
            <div class="col">
              <q-select
                dense
                rounded
                outlined
                v-model="pagination.sortBy"
                :options="sortOptions"
                :option-value="sortValue"
                :option-label="sortLabel"
                @update:model-value="tableRef.requestServerInteraction()"
              >
                <template v-slot:prepend>
                  <q-icon name="sort"></q-icon>
                </template>
              </q-select>
            </div>
            <div class="col">
              <q-input
                dense
                rounded
                outlined
                debounce="300"
                v-model="filter.title"
                placeholder="Search by title"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>
          </div>
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
            :task="props.row.task"
          ></model-card>
        </template>
      </q-table>
    </main>
  </div>
</template>

<script setup lang="ts">
import { QTableProps } from 'quasar';
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { onMounted, reactive, Ref, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import ModelCard from './ModelCard.vue';
import {
  FormOptionValue,
  Pagination,
  SearchFilter,
  SortOption,
} from './models';

export interface Props {
  rows?: ModelCardSummary[];
  cardClass?: string;
  showFilter?: boolean;
  filter: SearchFilter;
  pagination: Pagination;
}

// Router
const route = useRoute();
const router = useRouter();

// Stores
const modelStore = useModelStore();
const props = defineProps<Props>();

// Data Table
const tableRef = ref();
const rows: Ref<ModelCardSummary[]> = ref([]); // store data in table
const columns = [
  {
    name: 'title',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'title',
  },
  {
    name: 'task',
    required: false,
    label: 'Task',
    field: 'task',
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
const loading = ref(false);
const filter: SearchFilter = reactive(props.filter);

const pagination: Ref<Pagination> = ref(props.pagination);

const sortOptions = Object.freeze([
  {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true,
  },
  {
    label: 'Oldest Models (Last Updated)',
    value: 'lastModified',
    desc: false,
  },
  {
    label: 'Model Name (A-Z)',
    value: 'title',
    desc: false,
  },
]);

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
      // TODO: Show notification?
    });
}

function compositeId(row: ModelCardSummary): string {
  return `${row.creatorUserId}/${row.modelId}`;
}

function sortLabel(option: SortOption): string {
  return option.label;
}

function sortValue(option: SortOption): SortOption {
  return option;
}

function onSearchRequest(props: QTableProps): void {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy } =
    props.pagination as unknown as Pagination;
  loading.value = true;
  modelStore
    .getModels({
      p: page,
      n: rowsPerPage,
      sort: sortBy?.value ?? '_id',
      desc: sortBy?.desc ?? true,
      all: rowsPerPage === 0,
      ...filter,
    })
    .then(({ results, total }) => {
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total;
      pagination.value.page = page ?? 1;
      pagination.value.rowsPerPage = rowsPerPage ?? 0;
      pagination.value.sortBy = sortBy ?? {
        label: 'Last Created',
        value: '_id',
        desc: true,
      };
      pagination.value.descending = sortBy?.desc ?? true;
      loading.value = false;
      console.log(results);
    });
}

onMounted(() => {
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
  tableRef.value.requestServerInteraction();
});
</script>
