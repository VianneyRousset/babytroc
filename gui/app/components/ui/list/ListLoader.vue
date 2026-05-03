<template>
  <div class="ListLoader">
    <div class="skeleton-bar skeleton-pulse" />
    <div class="skeleton-bar skeleton-pulse" style="width: 70%;" />
    <div class="skeleton-bar skeleton-pulse" style="width: 85%;" />
  </div>
</template>

<style scoped lang="scss">
.ListLoader {
  @include flex-column;
  align-items: stretch;
  gap: $space-3;
  padding: $space-8 $space-4;

  .skeleton-bar {
    height: 16px;
    border-radius: $radius-sm;
    background: $divider;
  }
}
</style>
