<script setup lang="ts">
</script>

<template>
  <Slab>
    <slot />
    <template #image>
      <slot name="image" />
    </template>
  </Slab>
</template>

<style scoped lang="scss">
.MeSlab {
  @include flex-row;
  justify-content: space-between;
  gap: 1.25rem;
  font-size: 1.5rem;

  padding: 1rem 1.2rem;

  :deep(div) {
    flex: 1;
    position: relative;
    top: -2px;
  }

  :deep(svg:last-child) {
    color: $neutral-400;
  }
}
</style>
