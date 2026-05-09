<script setup lang="ts">
import { Ellipsis } from 'lucide-vue-next'

const open = defineModel<boolean>()

provide('dropdown-menu-open', open)
</script>

<template>
  <DropdownMenuRoot v-model:open="open">
    <!-- Trigger button -->
    <DropdownMenuTrigger class="DropdownMenuTrigger">
      <slot name="trigger">
        <Ellipsis
          style="cursor: pointer;"
          :size="32"
          :stroke-width="1.5"
        />
      </slot>
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <!-- Backdrop -->
      <div
        v-if="open"
        class="DropdownBackdrop"
      />
      <!-- Menu content -->
      <DropdownMenuContent
        class="DropdownMenuContent"
        :side-offset="0"
        :collision-padding="20"
        align="center"
      >
        <DropdownMenuArrow
          class="DropdownMenuArrow"
          :width="28"
          :height="14"
        />
        <slot />
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<style scoped lang="scss">
.DropdownMenuTrigger {
  @include reset-button;
}

:global(.DropdownBackdrop) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  inset: 0;
  z-index: 99;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
}

:deep(.DropdownMenuContent) {
  @include flex-column;
  align-items: stretch;

  z-index: 100;

  min-width: 260px;
  background: $bg-surface;
  border-radius: $radius-md;
  margin: 0;
  box-shadow: $shadow-lg;
}

:deep(.DropdownMenuArrow) {
  fill: $bg-surface;
}
</style>
