<script setup lang="ts">

import { Check, Clock } from 'lucide-vue-next';

const props = defineProps<{
  available: boolean,
  loading: boolean,
}>();

</script>

<template>

  <div v-if="props.available === true" class="availability available">
    <Check :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
    <p>Disponible</p>
  </div>

  <div v-else-if="props.available === false" class="availability unavailable === false">
    <Clock :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
    <p>Non-disponible</p>
  </div>


</template>

<style scoped lang="scss">
.availability {
  @include flex-row;
  font-family: 'Inter', sans-serif;

  gap: 0.6rem;
  font-size: 1.5rem;

  &.available {
    color: $primary-400;
  }

  &.unavailable {
    color: $red-800;
  }

  p {
    @include ellipsis-overflow;
  }
}
</style>
