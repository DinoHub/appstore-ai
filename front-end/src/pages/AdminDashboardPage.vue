<template>
  <q-page padding>
    <!-- content -->
    <main>
      <div class="row display-medium q-pl-md">Users</div>
      <section>
        <users-data-table :pagination="pagination"></users-data-table>
      </section>
    </main>
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-btn fab icon="add" color="tertiary" @click="persistent = true"></q-btn>
    </q-page-sticky>
  </q-page>

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
              matchPasswords(val) == true || `Both passwords fields must match`,
          ]"
        />
      </q-card-section>

      <q-card-actions align="left" class="q-pb-md q-pt-sm">
        <q-btn rounded outline class="text-red" label="Cancel" v-close-popup />
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
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { CreateUser, useUsersStore } from 'src/stores/users-store';
import { Pagination } from '../components/models';
import UsersDataTable from 'src/components/content/UsersDataTable.vue';
import { Notify } from 'quasar';

const authStore = useAuthStore();
const userStore = useUsersStore();

const persistent = ref(false);

const passwordErrorMsg = `Password must at least be
     length of 8, have 1 uppercase letter, 1 number and 1 special character`;

const pattern = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;

const createUser = ref({
  name: '',
  adminPriv: '',
  password: '',
  confirm_password: '',
});

function matchPasswords(str: string) {
  return str == createUser.value.password;
}

function callCreateUser() {
  
  userStore.createUser(
    createUser.value.name,
    createUser.value.adminPriv,
    createUser.value.password,
    createUser.value.confirm_password
  );
}

const pagination: Pagination = {
  sortBy: {
    label: 'Latest Models (Last Updated)',
    value: 'lastModified',
    desc: true,
  },
  descending: false,
  page: 1,
  rowsPerPage: 5,
  rowsNumber: 1,
};
</script>
