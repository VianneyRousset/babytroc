<template>
  <div class="List">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.List {
  @include flex-column;
  align-items: stretch;
  gap: var(--page-padding);

}
</style>
