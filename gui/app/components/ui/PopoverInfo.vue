<script setup lang="ts">
const open = defineModel<boolean>()
</script>

<template>
  <PopoverRoot
    :default-open="true"
  >
    <PopoverAnchor as-child>
      <slot />
    </PopoverAnchor>

    <PopoverPortal>
      <PopoverContent
      class="content"
      side="bottom"
      :side-offset="5"          
      >
      <slot name="info" />
      <PopoverArrow class="fill-white" />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>

<style scoped lang="scss">
:deep(.content) {
  @include flex-column;
  position: relative;
  background: white;
  z-index: 1000;
}
</style>
