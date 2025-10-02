<script setup lang="ts">
const slots = useSlots()
</script>

<template>
  <header class="AppHeaderDesktop">
    <div
      v-if="slots['buttons-left']"
      class="buttons left"
    >
      <slot name="buttons-left" />
    </div>
    <div
      class="content"
    >
      <slot />
    </div>
    <div
      v-if="slots['buttons-right']"
      class="buttons right"
    >
      <slot name="buttons-right" />
    </div>
  </header>
</template>

<style scoped lang="scss">
.AppHeaderDesktop {
  @include flex-row;
  gap: 1em;
  padding: 0 1em;

  div {
    gap: 1em;

    &.content {
      @include flex-column;
      align-items: center;
      padding: 1em;
      flex: 1;

      .SearchInput {
        width: 80%;
      }
    }

    &.buttons {
      @include flex-row;
      padding: 2em;

      &.left {
        padding-left: 0;
      }

      &.right {
        padding-right: 0;
      }
    }
  }
}
</style>
