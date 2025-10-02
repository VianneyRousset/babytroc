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
    <div class="content">
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

  .content {
    @include flex-column;
    align-items: stretch;
    gap: 1em;
    padding: 1em;

    & > :deep(.h) {
        @include flex-row;
        align-items: stretch;
        gap: 1em;
    }

    & > :deep(.golden-left) {
      & > *:nth-child(1) {
        flex: $golden-ratio;
      }

      & > *:nth-child(2) {
        flex: 1;
      }
    }

    & > :deep(.golden-right) {
      & > *:nth-child(1) {
        flex: 1;
      }

      & > *:nth-child(2) {
        flex: $golden-ratio;
      }
    }
  }
}
</style>
