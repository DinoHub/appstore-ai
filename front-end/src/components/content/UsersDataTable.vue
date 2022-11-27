<template>
  <div class="row">
    <q-drawer show-if-above :model-value="props.filterDrawer">
      <aside class="col-4 q-pt-md">
        <q-form class="q-px-md">
          <div class="text-h6">Query Filters</div>
          <q-expansion-item default-opened icon="account_box" label="User Type">
            <q-select
              v-model="userStore.privilege"
              :options="userStore.privilegeOptions"
              outlined
              hint="Select user privilege you want to view"
              class="q-ma-sm"
              color="primary"
            />
          </q-expansion-item>
          <q-expansion-item icon="calendar_month" label="Creation Date">
            <!-- ensure that then date display is fixed so it doenst look out of place -->
            <q-date v-model="userStore.createdDateRage" range color="primary" />
          </q-expansion-item>
        </q-form>
      </aside>
    </q-drawer>
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
    />
  </div>
</template>
<script setup lang="ts">
import { useUsersStore, Users } from 'src/stores/users-store';
import { onMounted, Ref, ref } from 'vue';
import { QTable, QTableColumn, QTableProps, Notify } from 'quasar';
import { Pagination, UsersSearchFilter } from './models';

export interface UsersDataTableProps {
  rows?: Users[];
  showFilter?: boolean;
  filterDrawer?: boolean;
  filter: UsersSearchFilter;
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

const onSearchRequest = (props: QTableProps) => {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy, descending } =
    props.pagination as unknown as Pagination;
  loading.value = true;
  userStore
    .getUsersPaginated(page, rowsPerPage, '', 2, sortBy, descending)
    .then(({ results, total_rows }) => {
      results.map((obj) => {
        if (obj.adminPriv == true) {
          obj.adminPriv = 'Admin';
        } else {
          obj.adminPriv = 'User';
        }

        return obj;
      });
      rows.value.splice(0, rows.value.length, ...results);
      pagination.value.rowsNumber = total_rows;
      pagination.value.page = page ?? 1;
      pagination.value.sortBy = sortBy;
      pagination.value.descending = descending;
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
