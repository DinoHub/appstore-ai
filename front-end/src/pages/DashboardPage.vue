<template>
  <q-page padding>
    <!-- content -->
    <div class="text-h3">Welcome Back, {{ username ?? 'User' }}</div>
    <main>
      <section>
        <div class="row">
          <div class="col col-sm-3 text-h4">Your models</div>
          <div class="col">
            <q-btn round icon="add" to="/models/create"></q-btn>
          </div>
          <div class="col">
            <q-btn to="/models" flat
              ><span class="underline">See all models</span></q-btn
            >
          </div>
        </div>
        <model-card></model-card>
      </section>
    </main>
  </q-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ModelCard from 'src/components/ModelCard.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useModelStore } from 'src/stores/model-store';

const authStore = useAuthStore();
const username = ref(authStore.user?.name);

// Get all user models
const modelStore = useModelStore();
// Get models owned by the user
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
