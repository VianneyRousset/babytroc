<script setup lang="ts">
import { Check, Clock } from 'lucide-vue-next'

const props = defineProps<{
  available: boolean
}>()

const { available } = toRefs(props)
</script>

<template>
  <div
    class="ItemAvailability"
    :class="{ available }"
  >
    <Check
      v-if="available"
      :size="32"
      :stroke-width="2"
    />
    <Clock
      v-else
      :size="32"
      :stroke-width="2"
    />
    <div>{{ available ? "Disponible" : "Non-disponible" }}</div>
  </div>
</template>

<style scoped lang="scss">
.ItemAvailability {
  @include flex-row;
  gap: 0.6rem;

  font-size: 1.5rem;
  font-family: "Inter", sans-serif;
  color: $red-800;

  &.available {
    color: $primary-400;
  }

  div {
    @include ellipsis-overflow;
  }
}
</style>
