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
</script>

<template>
  <NuxtLink
    class="DropdownMenuItem DropdownItem"
    :class="{ red }"
    :to="target ?? ''"
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
  </NuxtLink>
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

  &:first-of-type {
    border-top: none;
    border-radius: 8px 8px 0 0;
  }

  &:last-of-type {
    border-radius: 0 0 8px 8px;
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
