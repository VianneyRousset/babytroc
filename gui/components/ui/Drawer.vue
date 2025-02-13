<script setup lang="ts">

const model = defineModel<boolean>();

</script>

<template>

  <div :class="{ open: model }">
    <slot />
  </div>

</template>

<style scoped lang="scss">
div {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  z-index: 5;

  transition: 0.2s transform ease-out;
  transform: translate(100%, 0);

  &.open {
    transform: translate(0, 0);
  }
}
</style>
