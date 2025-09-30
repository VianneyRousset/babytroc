<script setup lang="ts">
import { Ellipsis } from 'lucide-vue-next'

const open = ref(false)
</script>

<template>
  <div class="DropdownMenu">
    <DropdownMenuRoot v-model:open="open">
      <!-- Trigger button -->
      <DropdownMenuTrigger class="DropdownMenuTrigger">
        <Ellipsis
          style="cursor: pointer;"
          :size="32"
          :stroke-width="2"
        />
      </DropdownMenuTrigger>

      <Overlay v-model="open">
        <DropdownMenuPortal>
          <!-- Menu content -->
          <DropdownMenuContent
            class="DropdownMenuContent"
            :side-offset="-10"
            align="start"
          >
            <slot />
            <DropdownMenuArrow
              class="DropdownMenuArrow"
              :width="28"
              :height="14"
            />
          </DropdownMenuContent>
        </DropdownMenuPortal>
      </Overlay>
    </DropdownMenuRoot>
  </div>
</template>

<style scoped lang="scss">
.DropdownMenuTrigger {
  @include reset-button;
}

:deep(.DropdownMenuContent) {
  @include flex-column;
  align-items: stretch;

  position: relative;

  min-width: 260px;
  background: white;
  border-radius: 0.5rem;
  margin: 0 6px;

  filter: drop-shadow(0px 0px 4px rgba(0, 0, 0, 0.25));

  &>div:not(a),
  &>a>div {
    @include flex-row;
    gap: 0.8rem;
    font-size: 1.5rem;

    justify-content: flex-start;
    cursor: pointer;
    color: $neutral-600;
    text-decoration: none;

    padding: 1rem 1.2rem;

    border-top: 1px solid $neutral-200;

    &:first-child {
      border-top: none;
    }

    &.red {
      color: $red-700;

      &:hover {
        color: $red-800;
      }
    }

    &:hover {
      color: $neutral-700;
    }
  }

}

:deep(.DropdownMenuArrow) {
  fill: white;
}
</style>
