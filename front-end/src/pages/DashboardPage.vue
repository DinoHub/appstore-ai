<template>
  <q-page padding>
    <!-- content -->
    <h1>Welcome Back, {{ username ?? 'User' }}</h1>
    <main>
      <section>
        <div class="row">
          <div class="col">
            <h2>Your models</h2>
          </div>
          <div class="col">
            <q-btn round icon="add"></q-btn>
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
modelStore.getAll().then((data) => {
  console.log(data);
});
// Get models owned by the user
</script>

<style>
.underline {
  text-decoration: underline;
}
</style>
