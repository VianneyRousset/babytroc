<script setup lang="ts">
import { Ellipsis } from 'lucide-vue-next'

const open = defineModel<boolean>()
</script>

<template>
  <DropdownMenuRoot v-model:open="open">
    <!-- Trigger button -->
    <DropdownMenuTrigger class="DropdownMenuTrigger">
      <slot name="trigger">
        <Ellipsis
          style="cursor: pointer;"
          :size="32"
          :stroke-width="2"
        />
      </slot>
    </DropdownMenuTrigger>

    <Teleport to="body">
      <Overlay v-model="open">
        <DropdownMenuPortal>
          <!-- Menu content -->
          <DropdownMenuContent
            class="DropdownMenuContent"
            :side-offset="0"
            align="start"
          >
            <DropdownMenuArrow
              class="DropdownMenuArrow"
              :width="28"
              :height="14"
            />
            <slot />
          </DropdownMenuContent>
        </DropdownMenuPortal>
      </Overlay>
    </Teleport>
  </DropdownMenuRoot>
</template>

<style scoped lang="scss">
.DropdownMenuTrigger {
  @include reset-button;
}

:deep(.DropdownMenuContent) {
  @include flex-column;
  align-items: stretch;

  z-index: 3;

  position: relative;

  min-width: 260px;
  background: white;
  border-radius: 8px;
  margin: 0 1em;

  filter: drop-shadow(0px 0px 4px rgba(0, 0, 0, 0.25));
}

.Overlay {
  z-index: 1;
}

:deep(.DropdownMenuArrow) {
  fill: white;
}
</style>
