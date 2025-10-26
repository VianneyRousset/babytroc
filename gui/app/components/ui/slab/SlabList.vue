<script setup lang="ts">
</script>

<template>
  <div class="SlabList">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.SlabList {
  display: grid;
  border-collapse: collapse;

  &>:deep(a > .Slab:not(:first-of-type)),
  &>:deep(.Slab:not(:first-of-type)) {
    border-top: 1px solid $neutral-200;
    margin-top: -1px;
  }

  &>:deep(a) {
    @include reset-link;
  }
}
</style>
