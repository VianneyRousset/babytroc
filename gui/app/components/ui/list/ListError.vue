<script setup lang="ts">
import { OctagonAlert } from 'lucide-vue-next'
</script>

<template>
  <div class="ListError">
    <OctagonAlert
      :size="24"
      :stroke-width="2"
    />
    <slot />
  </div>
</template>

<style lang="scss" scoped>
.ListError {
  @include flex-row;
  justify-content: center;
  gap: 1rem;
  margin-top: 2em;
  color: $red-700;
}
</style>
