<script setup lang="ts">
const slots = useSlots();

const props = defineProps<{
	maxWidth?: number;
}>();

const { maxWidth } = toRefs(props);
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
  display: flex;
  flex-direction: column;
  align-items: center;

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: $space-4;
    padding: 0 $space-6;
    height: 64px;
  }

  .content {
    box-sizing: border-box;
    width: 100%;
    max-width: v-bind("maxWidth ? `${maxWidth}px` : '1200px'");
    @include flex-column;
    align-items: stretch;
    gap: $space-4;
    padding: $space-4;

    @media (min-width: 1000px) {
      padding: $space-4 $space-6;
    }

    :deep(.legend) {
      font-style: italic;
      color: $text-secondary;
    }

    :deep(.h) {
      @include flex-row;
      align-items: stretch;
      gap: $space-4;
    }

    :deep(.v) {
      @include flex-column;
      align-items: stretch;
      gap: $space-4;
    }

    :deep(.golden-left) {
      & > *:nth-child(1) {
        flex: $golden-ratio;
      }

      & > *:nth-child(2) {
        flex: 1;
      }
    }

    :deep(.golden-right) {
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
