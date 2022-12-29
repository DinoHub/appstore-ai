<template>
  <q-page padding>
    <!-- content -->
    <main class="row justify-center items-center">
      <section class="col-5">
        <q-card tag="form" class="bg-surface">
          <q-card-section>
            <div class="text-h5">Login</div>
          </q-card-section>
          <q-card-section>
            <q-form @submit="onSubmit" class="q-gutter-md">
              <q-input
                filled
                v-model="userId"
                color="on-surface-variant"
                label="User ID"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'Please type a User ID',
                ]"
              ></q-input>
              <q-input
                filled
                color="on-surface-variant"
                v-model="password"
                label="Password"
                type="password"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'Please type a password',
                ]"
              ></q-input>
              <q-btn
                icon="login"
                label="Sign In"
                type="submit"
                color="primary"
                padding="sm xl"
                unelevated
                rounded
                no-caps
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

const onSubmit = async () => {
  if (userId.value && password.value) {
    await authStore.login(userId.value, password.value);
  }
};
</script>
