<script setup lang="ts">
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

<style scoped lang="scss">
.ListError {
  @include flex-column-center;
  padding: $space-16 $space-4;
  color: $text-secondary;
  text-align: center;
  font-size: 0.95rem;

  svg {
    color: $text-tertiary;
    margin-bottom: $space-4;
  }
}
</style>
