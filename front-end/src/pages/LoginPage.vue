<template>
  <q-page padding>
    <!-- content -->
    <main class="row justify-center items-center">
      <div class="col-4">
        <h1>Welcome to the AI App Store</h1>
      </div>
      <section class="col-4">
        <q-card tag="form">
          <q-card-section>
            <div class="text-h5">Login</div>
          </q-card-section>
          <q-card-section>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                outlined
                v-model="userId"
                label="User ID"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'Please type a User ID',
                ]"
              ></q-input>
              <q-input
                outlined
                v-model="password"
                label="Password"
                type="password"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'Please type a password',
                ]"
              ></q-input>
              <q-btn
                label="Login"
                type="submit"
                color="primary"
                padding="sm xl"
                rounded
              ></q-btn>
            </q-form>
          </q-card-section>
        </q-card>
      </section>
    </main>
  </q-page>
</template>

<script setup lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { Ref, ref } from 'vue';
const userId: Ref<string | null> = ref(null);
const password: Ref<string | null> = ref(null);
const authStore = useAuthStore();

async function onSubmit() {
  if (userId.value && password.value) {
    await authStore.login(userId.value, password.value);
  }
}
</script>
