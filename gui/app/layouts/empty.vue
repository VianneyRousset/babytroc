<template>
  <div class="layout">
    <slot />
  </div>
</template>

<style lang="scss" scoped>
.layout {
  @include flex-column;

  height: 100vh;
  box-sizing: border-box;
}
</style>
