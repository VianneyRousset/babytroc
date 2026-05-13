<script setup lang="ts">
const slots = useSlots();
const hasButtons = computed(() => !!slots['buttons-left'] || !!slots['buttons-right'])  
</script>

<template>
  <header
  class="AppHeaderDesktop"
  :class="{grid: hasButtons}"
  >
    <div
      v-if="hasButtons"
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
      v-if="hasButtons"
      class="buttons right"
    >
      <slot name="buttons-right" />
    </div>
  </header>
</template>

<style scoped lang="scss">
.AppHeaderDesktop {
  padding: 1em;

  &.grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
  }

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
      padding: 0;

      &.left {
        justify-content: flex-start;
      }

      &.right {
        justify-content: flex-end;
      }
    }
  }
}
</style>
