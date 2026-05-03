<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    position?: 'left' | 'right' | 'bottom'
  }>(), {
    position: 'left',
  },
)

const { position } = toRefs(props)

const model = defineModel<boolean>({ default: false })

const slots = useSlots()
const device = useDevice()

// On mobile, force bottom position for bottom-sheet behavior
const effectivePosition = computed(() =>
  device.isMobile ? 'bottom' : unref(position),
)
</script>

<template>
  <div
    class="Drawer"
    :class="{ open: model }"
    :position="effectivePosition"
  >
    <div
      v-if="effectivePosition === 'bottom'"
      class="drag-handle"
    />
    <div
      v-if="slots.header"
      class="header"
    >
      <slot name="header" />
    </div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.Drawer {
  position: fixed;
  box-sizing: border-box;
  background: $bg-surface;
  overflow-y: auto;
  z-index: 10;

  transition: transform 300ms $ease-spring;

  &[position=right] {
    top: 0;
    bottom: 0;
    right: 0;
    width: 90%;
    max-width: 400px;
    transform: translate(100%, 0);
    box-shadow: $shadow-lg;
  }

  &[position=left] {
    top: 0;
    bottom: 0;
    left: 0;
    width: 90%;
    max-width: 400px;
    transform: translate(-100%, 0);
    box-shadow: $shadow-lg;
  }

  &[position=bottom] {
    left: 0;
    right: 0;
    bottom: 0;
    max-height: 90vh;
    border-radius: $radius-lg $radius-lg 0 0;
    transform: translate(0, 100%);
    box-shadow: $shadow-lg;
  }

  &.open {
    transform: translate(0, 0);
  }

  .drag-handle {
    display: flex;
    justify-content: center;
    padding: $space-3 0;

    &::after {
      content: '';
      width: 36px;
      height: 4px;
      border-radius: 2px;
      background: #ddd;
    }
  }

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: $space-4;
    padding: 0 $space-4;
    height: 56px;
  }
}
</style>
