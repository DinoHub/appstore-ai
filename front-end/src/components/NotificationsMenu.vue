<template>
  <div>
    <q-btn flat round color="white" icon="chat">
      <q-menu>
        <q-item-label header>Notifications</q-item-label>
        <q-item
          clickable
          v-for="notification in notifications"
          :key="notification.id"
        >
          <q-item-section>
            <q-item-label>{{ notification.message }}</q-item-label>
            <q-item-label caption>{{ notification.createdAt }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-menu>
    </q-btn>
  </div>
</template>

<script setup lang="ts">
// TODO
</script>
