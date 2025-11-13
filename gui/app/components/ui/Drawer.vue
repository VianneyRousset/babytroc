<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    position?: 'left' | 'right'
  }>(), {
    position: 'left',
  },
)

const { position } = toRefs(props)

const model = defineModel<boolean>({ default: false })

const slots = useSlots()
</script>

<template>
  <div
    class="Drawer"
    :class="{ open: model }"
    :position="position"
  >
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
  top: 0;
  bottom: 0;
  right: 0;

  width: 90%;
  max-width: 400px;
  overflow-y: scroll;

  box-sizing: border-box;

  background: white;

  transition: 0.2s transform ease-out;

  &[position=right] {
    transform: translate(100%, 0);
  }

  &[position=left] {
    transform: translate(-100%, 0);
  }

  &.open {
    transform: translate(0, 0);
    @include bar-shadow;
  }

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: 16px;
    padding: 0 1rem;
    height: 64px;
  }
}
</style>
