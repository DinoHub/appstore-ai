<template>
  <div>My component</div>
  <iframe width="76%" height="700"
   src="http://ie-inception.inference-engine.172.20.255.202.sslip.io/"
  ></iframe>
</template>

<script lang="ts">
import { defineComponent, defineProps } from 'vue'
const props = defineProps({
  url : String
})
export default defineComponent({
  // name: 'ComponentName'

})

</script>
