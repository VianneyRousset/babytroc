<template>
  <div class="CheckboxGroup">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.CheckboxGroup {
  @include flex-column;
  align-items: stretch;
  gap: 0.5em;
}
</style>
