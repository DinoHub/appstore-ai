<template>
  <!-- Use breadcrumbs to show user where they are in the site -->
  <q-breadcrumbs class="text-primary">
    <q-breadcrumbs-el
      :label="crumb.label"
      :to="crumb.to"
      v-for="crumb in breadcrumbs"
      :key="crumb.to"
    />
  </q-breadcrumbs>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { Breadcrumb } from 'src/components/models';

const route = useRoute();

const breadcrumbs = computed(() => {
  const router = useRouter();
  const output: Breadcrumb[] = [];
  const path = route.fullPath.split('/');
  let cumulativePath = '';
  path.shift(); // remove first part of path
  path.forEach((p) => {
    cumulativePath += `/${p}`;
    output.push({
      label: (router.resolve(cumulativePath).name as string) ?? p,
      to: cumulativePath,
    });
  });
  return output;
});
</script>
