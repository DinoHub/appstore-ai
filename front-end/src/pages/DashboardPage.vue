<template>
  <q-page padding>
    <!-- content -->
    <div class="text-h3">Welcome Back, {{ username ?? 'User' }}</div>
    <main>
      <section>
        <div class="row"></div>
        <model-card-data-table
          :pagination="pagination"
          :filter="filter"
          card-class="col-xs-12 col-sm-6 col-md-3 col-xl-4"
        >
          <template v-slot:top-left>
            <div class="row content-stretch">
              <div class="col col-sm-5 text-h4">Your Models</div>
              <div class="col col-sm-2">
                <q-btn round icon="add" to="/models/create"></q-btn>
              </div>
              <div class="col col-sm-5">
                <router-link class="text-body2" to="/models"
                  >View all models</router-link
                >
              </div>
            </div>
          </template>
        </model-card-data-table>
      </section>
    </main>
  </q-page>
</template>

<script setup lang="ts">
import { ref, Ref } from 'vue';
import ModelCardDataTable from 'src/components/ModelCardDataTable.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { ModelCardSummary, useModelStore } from 'src/stores/model-store';
import { Pagination, SearchFilter } from '../components/models';

const authStore = useAuthStore();
const username = ref(authStore.user?.name);

// Get all user models
const filter: SearchFilter = {
  tags: [],
  tasks: [],
  frameworks: [],
  creator: authStore.user?.userId,
};

const pagination: Pagination = {
  sortBy: '_id',
  descending: false,
  page: 1,
  rowsPerPage: 6,
  rowsNumber: 1,
};
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
