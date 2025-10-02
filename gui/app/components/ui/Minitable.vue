<template>
  <div class="Minitable">
    <slot />
  </div>
</template>

<style lang="scss" scoped>
.Minitable {
  display: grid;
  gap: 1em;
  grid-template-columns: 1fr 3fr;
  margin-bottom: 2em;

  :deep(.label) {
    color: $neutral-400;
  }

  :deep(ul) {
    @include reset-list;
    @include flex-column;
    gap: 0.5em;
    align-items: flex-start;
  }
}
</style>
