<script setup lang="ts">
const props = withDefaults(defineProps<{
  light?: boolean
}>(), {
  light: false,
})

const { light } = toRefs(props)
</script>

<template>
  <div
    class="SlabList"
    :class="{ light }"
  >
    <slot />
  </div>
</template>

<style scoped lang="scss">
.SlabList {
  @include flex-column;
  align-items: stretch;

  & > :deep(.Slab) {

    margin-top: -1px;
    margin-left: -1px;
    margin-right: -1px;
    border: 1px solid $neutral-200;
    border-left-color: transparent;
    border-right-color: transparent;
  }

  &.light>:deep(.Slab) {
    &:first-child {
      border-top-color: transparent;
    }

    &:last-child {
      border-bottom-color: transparent;
    }
  }

  &>:deep(a) {
    @include reset-link;
  }
}
</style>
