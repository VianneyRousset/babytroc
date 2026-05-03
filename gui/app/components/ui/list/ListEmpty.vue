<template>
  <div class="ListEmpty">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.ListEmpty {
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
