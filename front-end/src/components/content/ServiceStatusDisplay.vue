<template>
  <!-- Component that displays data from inference service status endpoint -->
  <q-markup-table wrap-cells>
    <thead>
      <tr>
        <th colspan="2">Service Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Status</td>
        <td>{{ props.status?.status }}</td>
      </tr>
      <tr>
        <td>Service Name</td>
        <td>{{ props.status?.serviceName }}</td>
      </tr>
      <tr>
        <td>Ready?</td>
        <td>{{ props.status?.ready }}</td>
      </tr>
      <tr>
        <td>Schedulable in Cluster?</td>
        <td>{{ props.status?.schedulable }}</td>
      </tr>
      <tr>
        <td>Expected Instances/Replicas</td>
        <td>{{ props.status?.expectedReplicas }}</td>
      </tr>
      <tr>
        <td>Details</td>
        <td>{{ props.status?.message }}</td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script setup lang="ts">
import { InferenceServiceStatus } from 'src/stores/inference-service-store';

export interface ServiceStatusDisplayProps {
  status?: InferenceServiceStatus | null;
}

const props = defineProps<ServiceStatusDisplayProps>();
</script>
