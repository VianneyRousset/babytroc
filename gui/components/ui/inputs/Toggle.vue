<script setup lang="ts">
const model = defineModel<boolean>();
</script>

<template>

  <div @click="model = !model">
    <slot />
  </div>

</template>

<style scoped lang="scss">
div {
  cursor: pointer;
}
</style>
