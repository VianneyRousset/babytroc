<script setup lang="ts">
</script>

<template>
  <div class="SlabList">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.SlabList {
  @include flex-column;
  align-items: stretch;

  &>:deep(a:not(:last-child) > .Slab),
  &>:deep(.Slab:not(:last-child)) {
    border-bottom: 1px solid $neutral-200;
  }

  &>:deep(a) {
    @include reset-link;
  }
}
</style>
