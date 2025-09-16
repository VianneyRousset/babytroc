<script setup lang="ts">
const slots = useSlots()
</script>

<template>
  <div class="Panel">
    <div
      v-if="slots.header"
      class="header"
    >
      <slot name="header" />
    </div>
    <div>
      <slot />
    </div>
  </div>
</template>

<style scoped lang="scss">
.Panel {

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: 16px;
    padding: 0 1rem;
    height: 64px;
  }

  div:not(.header) {
    padding: 1em;
  }
}
</style>
