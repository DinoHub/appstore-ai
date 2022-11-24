<template>
  <q-drawer show-if-above>
    <aside class="col col-sm-3 q-pt-md">
      <q-form class="q-px-md">
        <div class="text-h6">Query Filters</div>
      </q-form>
    </aside>
  </q-drawer>
  <div class="row">
    <div class="col-8 q-ml-md q-mb-lg"></div>
  </div>
  <div class="row">
    <q-table
      class="col-10 q-ml-md"
      ref="tableRef"
      rows-per-page-label="Users per page:"
      :rows="rows"
      :columns="columns"
      :filter="filter"
      :loading="loading"
      row-key="userId"
      v-model:pagination="pagination"
      v-model:selected="selected"
      selection="multiple"
      @request="onSearchRequest"
      @selection="test"
    />
  </div>
</template>
<script setup lang="ts">
import { useUsersStore, Users } from 'src/stores/users-store';
import { onMounted, reactive, Ref, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { QTable, QTableColumn, QTableProps, Notify } from 'quasar';
import { Pagination, SearchFilter } from './models';

export interface UsersDataTableProps {
  rows?: Users[];
  cardClass?: string;
  cardContainerClass?: string;
  showFilter?: boolean;
  filterDrawer?: boolean;
  filter: SearchFilter;
  pagination: Pagination;
}

const userStore = useUsersStore();
const props = defineProps<UsersDataTableProps>();
const pagination: Ref<Pagination> = ref(props.pagination);

// Data Table
const tableRef: Ref<QTable | undefined> = ref();
const rows: Ref<Users[]> = ref([]); // store data in table
const loading = ref(false);

const selected = ref([]);

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
    name: 'name',
    required: true,
    label: 'Name',
    field: 'name',
    sortable: true,
  },
  {
    name: 'adminPriv',
    required: true,
    label: 'Permissions',
    field: 'adminPriv',
    sortable: true,
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

function test() {
  console.log('hello');
}

const onSearchRequest = (props: QTableProps) => {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy } =
    props.pagination as unknown as Pagination;
  loading.value = true;
  userStore
    .getUsersPaginated(page, rowsPerPage, '', 2)
    .then(({ results, total }) => {
      results.map((obj) => {
        if (obj.adminPriv == true) {
          obj.adminPriv = 'Admin';
        } else {
          obj.adminPriv = 'User';
        }
        // var createdDate = new Date(obj.created);
        // obj.created = `${createdDate.getDate()}/${
        //   createdDate.getMonth() + 1
        // }/${createdDate.getFullYear()}, ${createdDate.toLocaleTimeString(
        //   'en-US',
        //   { hour12: false }
        // )}`;
        // var modifiedDate = new Date(obj.lastModified);
        // obj.lastModified = `${modifiedDate.getDate()}/${
        //   modifiedDate.getMonth() + 1
        // }/${modifiedDate.getFullYear()}, ${modifiedDate.toLocaleTimeString(
        //   'en-US',
        //   { hour12: false }
        // )}`;

        return obj;
      });
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total;
      pagination.value.page = page ?? 1;
      pagination.value.rowsPerPage = rowsPerPage ?? 0;
      loading.value = false;
    });
};

onMounted(() => {
  // TODO: overhaul this?
  // If URL contains filter params, auto add
  // Update table with latest value from Server
  tableRef.value?.requestServerInteraction();
});
</script>
