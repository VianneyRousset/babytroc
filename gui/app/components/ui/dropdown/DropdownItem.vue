<script setup lang="ts">
import type { LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(defineProps<{
  target?: string | RouteLocationGeneric
  icon?: LucideIcon
  red?: boolean
}>(), {
  red: false,
})

const { target, icon, red } = toRefs(props)

const menuOpen = inject('dropdown-menu-open')
const NuxtLink = resolveComponent('NuxtLink')
</script>

<template>
  <component
    :is="target ? NuxtLink : 'div'"
    class="DropdownMenuItem DropdownItem"
    :class="{ red }"
    :to="target"
    @click="() => (menuOpen = false)"
  >
    <component
      :is="icon"
      v-if="icon"
      :size="32"
      :stroke-width="1.5"
    />
    <div>
      <slot />
    </div>
  </component>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}

.DropdownMenuItem {
  @include flex-row;
  gap: 0.8rem;
  font-size: 1.5rem;

  justify-content: flex-start;
  cursor: pointer;
  color: $neutral-600;
  text-decoration: none;
  user-select: none;
  user-drag: none;

  padding: 1rem 1.2rem;

  border-top: 1px solid $neutral-200;

  /* not the 1st child as it is the DropdownMenuArrow */
  &:nth-child(2) {
    border-top: none;
    border-top-left-radius: 8px 8px;
    border-top-right-radius: 8px 8px;
  }

  &:last-child {
    border-bottom-left-radius: 8px 8px;
    border-bottom-right-radius: 8px 8px;
  }

  &:hover {
    background: $neutral-50;
  }

  &:active {
    background: $neutral-200;
    color: $neutral-800;
  }

  &.red {
    color: $red-700;
  }

  &.red:hover {
    background: $red-50;
  }

  &.red:active {
    background: $red-200;
    color: $red-800;
  }

}
</style>
