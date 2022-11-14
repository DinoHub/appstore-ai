<style>
.q-table__grid-content {
  justify-content: center;
}
</style>
<template>
  <div class="row">
    <q-drawer show-if-above :model-value="props.filterDrawer" v-if="showFilter">
      <aside class="col col-sm-3 q-pt-md">
        <q-form class="q-px-md">
          <div class="text-h6">Query Filters</div>
          <q-expansion-item default-opened icon="task" label="Task">
            <q-option-group
              v-model="filter.tasks"
              :options="tasks"
              color="primary"
              type="checkbox"
            ></q-option-group>
          </q-expansion-item>
          <q-expansion-item icon="code" label="Frameworks">
            <q-option-group
              v-model="filter.frameworks"
              :options="frameworks"
              color="primary"
              type="checkbox"
            ></q-option-group>
          </q-expansion-item>
          <q-expansion-item default-opened icon="tag" label="Tags">
            <q-select
              hint="Type in tags or use dropdown to add available tags"
              class="q-ma-sm"
              color="secondary"
              v-model="filter.tags"
              use-input
              use-chips
              multiple
              autogrow
              outlined
              input-debounce="500"
              new-value-mode="add-unique"
              :options="tags"
            ></q-select>
          </q-expansion-item>
        </q-form>
      </aside>
    </q-drawer>

    <main class="col">
      <q-table
        grid
        ref="tableRef"
        rows-per-page-label="Models per page:"
        :rows="rows"
        :columns="columns"
        :row-key="compositeId"
        :filter="filter"
        :loading="loading"
        @request="onSearchRequest"
        v-model:pagination="pagination"
      >
        <template v-slot:top-left>
          <slot name="top-left"></slot>
        </template>
        <template v-slot:top-right>
          <div class="row q-gutter-md">
            <div class="col-auto">
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
            <div class="col-auto">
              <q-input
                dense
                rounded
                outlined
                autofocus=""
                debounce="500"
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
          <div :class="cardContainerClass ?? ''">
            <model-card
              :card-class="cardClass ?? ''"
              :title="props.row.title"
              :model-id="props.row.modelId"
              :creator-user-id="props.row.creatorUserId"
              :tags="props.row.tags"
              :frameworks="props.row.frameworks"
              :description="props.row.description"
              :task="props.row.task"
            ></model-card>
          </div>
        </template>
      </q-table>
    </main>
  </div>
</template>

<script setup lang="ts">
import { QTableProps } from 'quasar';
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { onMounted, reactive, Ref, ref, watch } from 'vue';
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
  cardContainerClass?: string;
  showFilter?: boolean;
  filterDrawer?: boolean;
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
