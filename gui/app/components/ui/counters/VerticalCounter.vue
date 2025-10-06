<script setup lang="ts">
const model = defineModel<number>()
</script>

<template>
  <div class="VerticalCounter">
    <div>{{ model ?? '...' }}</div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.VerticalCounter {
  @include flex-column;
  justify-content: center;
  gap: 0.6em;

  color: $neutral-700;
  min-width: 8em;

  & > *:last-child {
    @include font-inter;
    font-size: 4em;
  }

  & > *:last-child {
    @include font-jakarta;
  }
}
</style>
