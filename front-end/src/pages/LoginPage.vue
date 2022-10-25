<template>
  <q-page padding>
    <!-- content -->
    <main class="row">
      <div class="col">
        <h1>Welcome to the AI App Store</h1>
      </div>
      <section class="col">
        <q-card tag="form">
          <q-card-section>
            <h4>Login</h4>
          </q-card-section>
          <q-card-section>
            <q-form @submit="onSubmit">
              <q-input
                v-model="userId"
                label="User ID"
                lazy-rules
                :rules="[
                  (val) => (val && val.length > 0) || 'Please type a User ID',
                ]"
              ></q-input>
              <q-input
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
                icon="login"
                type="submit"
                color="primary"
              ></q-btn>
            </q-form>
          </q-card-section>
        </q-card>
      </section>
    </main>
  </q-page>
</template>

<script lang="ts">
import { useAuthStore } from 'src/stores/auth-store';
import { defineComponent, Ref, ref } from 'vue';
const userId: Ref<string | null> = ref(null);
const password: Ref<string | null> = ref(null);
const authStore = useAuthStore();

async function onSubmit() {
  if (userId.value && password.value) {
    await authStore.login(userId.value, password.value);
  }
}

export default defineComponent({
  setup() {
    return {
      userId,
      password,
      onSubmit,
    };
  },
});
</script>
