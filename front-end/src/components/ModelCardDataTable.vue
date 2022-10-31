<template>
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
  >
    <template v-slot:top-left>
      <slot name="top-left"></slot>
    </template>
    <template v-slot:top-right>
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
</template>

<script setup lang="ts">
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { onMounted, reactive, Ref, ref } from 'vue';
import { useRoute } from 'vue-router';
import ModelCard from './ModelCard.vue';
import { Pagination, SearchFilter } from './models';

export interface Props {
  rows?: ModelCardSummary[];
  cardClass: string;
}

const props = defineProps<Props>();
const route = useRoute();

const tableRef = ref();
const filter: SearchFilter = reactive({});
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
