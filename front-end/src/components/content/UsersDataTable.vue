<template>
  <div class="row ">
    <q-drawer show-if-above :model-value="props.filterDrawer" class="">
      <aside class="col-4 q-pt-md">
        <q-form>
          <div class="text-h6 q-pl-md">Query Filters</div>
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
          <q-expansion-item icon="calendar_month" label="Date Created">
            <q-date
              v-model="userStore.createdDateRange"
              range
              minimal
              color="primary"
              class="q-mt-sm q-ml-sm q-mb-sm"
            />
          </q-expansion-item>
          <q-expansion-item icon="event" label="Last Modified">
            <q-date
              v-model="userStore.lastModifiedRange"
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
      rows-per-page-label="Users per page:"
      :rows-per-page-options="[5, 7, 10, 15, 20, 25, 50]"
      :rows="rows"
      :columns="columns"
      :filter="userStore"
      :loading="loading"
      row-key="userId"
      v-model:pagination="pagination"
      v-model:selected="selected"
      selection="multiple"
      @request="onSearchRequest"
    >
      <template v-slot:top>
        <q-btn
          class="q-ml-sm"
          color="primary"
          v-if="selected.length > 0"
          :label="`Edit (${selected.length})`"
          @click="openEditPopup"
        />
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
            v-model="userStore.idSearch"
            label=""
            type="search"
          >
            <template v-if="userStore.idSearch" v-slot:append>
              <q-icon
                name="close"
                @click.stop.prevent="userStore.idSearch = ''"
              />
            </template>
            <template v-slot:before>
              <q-icon name="search" />
            </template>
          </q-input>
        </form>
        <form autocomplete="off" style="width: 22.5%">
          <q-input
            hint="Search By Name"
            dense
            label=""
            debounce="700"
            color="primary"
            v-model="userStore.nameSearch"
            type="search"
          >
            <template v-if="userStore.nameSearch" v-slot:append>
              <q-icon
                name="close"
                @click.stop.prevent="userStore.nameSearch = ''"
              />
            </template>
            <template v-slot:before>
              <q-icon name="search" />
            </template>
          </q-input>
        </form>
      </template>
    </q-table>
  </div>

  <q-page-sticky position="bottom-right" :offset="[18, 18]">
    <q-btn fab icon="add" color="tertiary" @click="persistent = true"></q-btn>
  </q-page-sticky>

  <q-dialog
    v-model="persistent"
    persistent
    transition-show="scale"
    transition-hide="scale"
  >
    <q-card class="q-px-lg" style="width: 100%">
      <q-card-section class="q-pb-sm">
        <div class="text-h6 q-mb-md">Create User</div>
        <q-input
          filled
          class="q-mb-md q-pb-md"
          color="on-surface-variant"
          label="User ID"
          placeholder="Will be auto-generated if left blank"
          v-model="createUser.userId"
        />
        <q-input
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Username"
          v-model="createUser.name"
          lazy-rules
          :rules="[
            (val) => (val && val.length > 0) || 'Please type a username',
          ]"
        />
        <q-select
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Permissions"
          :options="['Admin', 'User']"
          lazy-rules
          v-model="createUser.adminPriv"
          :rules="[
            (val) =>
              val != 'Admin' || val != 'User' || 'Select a permission type',
          ]"
        ></q-select>
        <q-input
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Password"
          type="password"
          v-model="createUser.password"
          lazy-rules
          :rules="[
            (val) =>
              (pattern.test(val) == true &&
                /[A-Z]/.test(val) == true &&
                /\d/.test(val) == true &&
                val.length >= 8) ||
              passwordErrorMsg,
          ]"
        />
        <q-input
          filled
          color="on-surface-variant"
          label="Confirm Password"
          v-model="createUser.confirm_password"
          lazy-rules
          type="password"
          :rules="[
            (val) =>
              matchPasswords(val, createUser) == true ||
              `Both passwords fields must match`,
          ]"
        />
      </q-card-section>

      <q-card-actions align="left" class="q-pb-md q-pt-sm">
        <q-btn
          rounded
          outline
          class="text-red"
          label="Cancel"
          v-close-popup
          @click="clearCreateUser()"
        />
        <q-space />
        <q-btn
          rounded
          outline
          class="text-primary"
          label="Create user"
          @click="callCreateUser()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="removePopup" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Remove Users</div>
        <q-list>
          <q-item-label header class="text-black text-bold q-pl-none"
            >Deleting {{ selected.length }} user(s):</q-item-label
          ><q-item
            v-for="x in selected"
            :key="x.userId"
            class="q-pl-none q-pt-none"
          >
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" icon="person" />
            </q-item-section>

            <q-item-section>
              {{ x.name }} {{ ` (${x.userId})` }}
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
          @click="callDeleteUsers"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="editMultiPopup" persistent>
    <q-card>
      <q-card-section>
        <div class="text-h6">Edit Users</div>
        <q-list>
          <q-item-label header class="text-black text-bold q-pl-none"
            >Editing {{ selected.length }} user(s):</q-item-label
          ><q-item
            v-for="x in selected"
            :key="x.userId"
            class="q-pl-none q-pt-none"
          >
            <q-item-section avatar>
              <q-avatar color="primary" text-color="white" icon="person" />
            </q-item-section>

            <q-item-section>
              {{ x.name }} {{ ` (${x.userId})` }}
            </q-item-section>
          </q-item>
        </q-list>
        <q-select
          dense
          class="q-mt-lg"
          color="on-surface-variant"
          hint="Permissions"
          :options="[
            {
              value: 1,
              label: 'Admin',
            },
            {
              value: 0,
              label: 'User',
            },
          ]"
          lazy-rules
          v-model="editManyUsers"
          :rules="[
            (val) =>
              val != 'Admin' || val != 'User' || 'Select a permission type',
          ]"
        ></q-select>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          rounded
          outline
          label="Cancel"
          padding="sm md"
          color="error"
          v-close-popup
          @click="exitMultiEdit"
        />
        <q-space />
        <q-btn
          rounded
          label="Confirm"
          color="primary"
          padding="sm md"
          outline
          @click="callMultiEditUsers"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog
    v-model="editSinglePopup"
    persistent
    transition-show="scale"
    transition-hide="scale"
  >
    <q-card class="q-px-lg" style="width: 100%">
      <q-card-section class="q-pb-sm">
        <div class="text-h6 q-mb-md">Edit User</div>
        <q-input
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Username"
          v-model="editUser.name"
          lazy-rules
          :rules="[
            (val) => (val && val.length > 0) || 'Please type a username',
          ]"
        />
        <q-select
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Permissions"
          :options="['Admin', 'User']"
          lazy-rules
          v-model="editUser.adminPriv"
          :rules="[
            (val) =>
              val != 'Admin' || val != 'User' || 'Select a permission type',
          ]"
        ></q-select>
        <q-input
          filled
          class="q-mb-md"
          color="on-surface-variant"
          label="Password"
          type="password"
          v-model="editUser.password"
          lazy-rules
          :rules="[
            (val) =>
              (pattern.test(val) == true &&
                /[A-Z]/.test(val) == true &&
                /\d/.test(val) == true &&
                val.length >= 8) ||
              passwordErrorMsg,
          ]"
        />
        <q-input
          filled
          color="on-surface-variant"
          label="Confirm Password"
          v-model="editUser.confirm_password"
          lazy-rules
          type="password"
          :rules="[
            (val) =>
              matchPasswords(val, editUser) == true ||
              `Both passwords fields must match`,
          ]"
        />
      </q-card-section>

      <q-card-actions align="left" class="q-pb-md q-pt-sm">
        <q-btn
          rounded
          outline
          class="text-red"
          label="Cancel"
          v-close-popup
          @click="clearEditUser()"
        />
        <q-space />
        <q-btn
          rounded
          outline
          class="text-primary"
          label="Update user"
          @click="callEditUser()"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { useUsersStore, Users } from 'src/stores/users-store';
import { onMounted, Ref, ref } from 'vue';
import { Notify, QTable, QTableColumn, QTableProps } from 'quasar';
import { Pagination, UsersSearchFilter } from './models';

export interface UsersDataTableProps {
  rows?: Users[];
  showFilter?: boolean;
  filterDrawer?: boolean;
  filter: UsersSearchFilter;
  pagination: Pagination;
}

const persistent = ref(false);

const passwordErrorMsg = `Password must at least be
     length of 8, have 1 uppercase letter, 1 number and 1 special character`;

const pattern = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;

const createUser = ref({
  userId: '',
  name: '',
  adminPriv: '',
  password: '',
  confirm_password: '',
});
const editUser = ref({
  name: '',
  adminPriv: '',
  password: '',
  confirm_password: '',
});
const selected = ref([]);
const removePopup = ref(false);
const editMultiPopup = ref(false);
const editSinglePopup = ref(false);
const editManyUsers = ref('');

// Stores & Props
const userStore = useUsersStore();
const props = defineProps<UsersDataTableProps>();
const pagination: Ref<Pagination> = ref(props.pagination);
pagination.value.rowsPerPage = 10;

// Data Table
const tableRef: Ref<QTable | undefined> = ref();
const rows: Ref<Users[]> = ref([]); // store data in table
const loading = ref(false);

function matchPasswords(str: string, other_value: any) {
  return str == other_value.password;
}

function openEditPopup() {
  if (selected.value.length == 1) {
    editUser.value.name = selected.value[0].name;
    editUser.value.adminPriv = selected.value[0].adminPriv;
    editSinglePopup.value = true;
  } else if (selected.value.length > 1) {
    editMultiPopup.value = true;
  } else {
    console.warn('Error with popup control');
  }
}

function exitMultiEdit() {
  editManyUsers.value = '';
}

function callMultiEditUsers() {
  if (editManyUsers.value != 1 && editManyUsers.value != 0) {
    Notify.create({
      message: 'Set value for permssions to update users to!',
      type: 'warning',
    });
  } else {
    userStore
      .editUsersMulti(selected.value, editManyUsers.value)
      .then(() => {
        editMultiPopup.value = false;
        editManyUsers.value = '';
        tableRef.value?.requestServerInteraction();
      })
      .catch((err) => {
        Notify.create({
          message: 'Failed to update users',
          type: 'negative',
        });
        console.error(err);
      });
  }
}

function callEditUser() {
  if (
    editUser.value.name.trim() == '' ||
    (editUser.value.adminPriv.toLowerCase() != 'admin' &&
      editUser.value.adminPriv.toLowerCase() != 'user') ||
    editUser.value.password.trim() == '' ||
    editUser.value.confirm_password.trim() == ''
  ) {
    Notify.create({
      type: 'negative',
      message: 'Fill in all required fields',
    });
  } else if (editUser.value.password != editUser.value.confirm_password) {
    Notify.create({
      type: 'negative',
      message: 'Ensure both password fields match',
    });
  } else {
    userStore
      .editUser(
        selected.value[0].userId,
        editUser.value.name,
        editUser.value.adminPriv,
        editUser.value.password,
        editUser.value.confirm_password
      )
      .then(() => {
        clearEditUser();
        tableRef.value?.requestServerInteraction();
        editSinglePopup.value = false;
      })
      .catch((err) => {
        Notify.create({
          message: 'Failed to update user',
          type: 'negative',
        });
        console.error(err);
      });
  }
}

function callDeleteUsers() {
  userStore
    .removeUsers(selected.value)
    .then(() => {
      selected.value = [];
      tableRef.value?.requestServerInteraction();
    })
    .catch((err) => {
      Notify.create({
        message: 'Failed to delete users',
        type: 'negative',
      });
      console.error(err);
    });
}

function callCreateUser() {
  if (
    createUser.value.name.trim() == '' ||
    (createUser.value.adminPriv.toLowerCase() != 'admin' &&
      createUser.value.adminPriv.toLowerCase() != 'user') ||
    createUser.value.password.trim() == '' ||
    createUser.value.confirm_password.trim() == ''
  ) {
    Notify.create({
      type: 'negative',
      message: 'Fill in all required fields',
    });
  } else if (createUser.value.password != createUser.value.confirm_password) {
    Notify.create({
      type: 'negative',
      message: 'Ensure both password fields match',
    });
  } else {
    userStore
      .createUser(
        createUser.value.userId,
        createUser.value.name,
        createUser.value.adminPriv,
        createUser.value.password,
        createUser.value.confirm_password
      )
      .then(() => {
        clearCreateUser();
        tableRef.value?.requestServerInteraction();
        persistent.value = false;
      })
      .catch((err) => {
        persistent.value = true;
      });
  }
}

function clearEditUser() {
  editUser.value.name = '';
  editUser.value.adminPriv = '';
  editUser.value.password = '';
  editUser.value.confirm_password = '';
}

function clearCreateUser() {
  createUser.value.userId = '';
  createUser.value.name = '';
  createUser.value.adminPriv = '';
  createUser.value.password = '';
  createUser.value.confirm_password = '';
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

// search request function to get users from the backend
const onSearchRequest = (props: QTableProps) => {
  if (!props.pagination) {
    return;
  }
  const { page, rowsPerPage, sortBy, descending } =
    props.pagination as unknown as Pagination;
  selected.value = [];
  loading.value = true;
  userStore
    .getUsersPaginated(page, rowsPerPage, sortBy, descending)
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
      pagination.value.rowsPerPage = rowsPerPage ?? 10;
      loading.value = false;
    })
    .catch((err) => {
      Notify.create({
        message: 'Failed to get users',
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
