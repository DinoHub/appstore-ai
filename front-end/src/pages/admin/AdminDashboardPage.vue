<template>
  <div>
    <q-page padding>
      <!-- content -->
      <main>
        <div class="row justify-center">
          <div class="col-11 display-medium q-pl-md q-mt-xl">Users</div>
        </div>
        <section>
          <users-data-table
            :pagination="pagination"
            :filter-drawer="filterDrawer"
          ></users-data-table>
        </section>
      </main>
    </q-page>
    <q-page-sticky position="top-left" :offset="[7, 10]">
      <q-btn
        fab-mini
        :icon="filterDrawer ? 'keyboard_arrow_left' : 'keyboard_arrow_right'"
        color="tertiary"
        @click="filterDrawer = !filterDrawer"
      ></q-btn>
    </q-page-sticky>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useUsersStore } from 'src/stores/users-store';
import { Pagination } from 'src/components/components/models';
import UsersDataTable from 'src/components/content/UsersDataTable.vue';

const filterDrawer = ref(true);
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
