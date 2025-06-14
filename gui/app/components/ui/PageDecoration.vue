<template>
  <div class="PageDecoration">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.PageDecoration {
  @include flex-column-center;
  padding: 4rem 0;
  color: $neutral-600;
}
</style>
