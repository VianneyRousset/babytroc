<script setup lang="ts">
import { Square, type LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(
  defineProps<{
    active?: boolean
    disabled?: boolean
    icon?: LucideIcon
    target?: string | RouteLocationGeneric
    size?: number
    strokeWidth?: number
    absoluteStrokeWidth?: boolean
  }>(),
  {
    active: false,
    disabled: false,
    size: 32,
  },
)

const { disabled, active, icon, target, size, strokeWidth, absoluteStrokeWidth } = toRefs(props)

const NuxtLink = resolveComponent('NuxtLink')
</script>

<template>
  <component
    :is="target ? NuxtLink : 'div'"
    class="IconButton"
    role="button"
    :disabled="disabled"
    :active="active"
    :to="target"
  >
    <component
      :is="icon"
      v-if="icon"
      :size="size"
      :stroke-width="strokeWidth"
      :absolute-stroke-width="absoluteStrokeWidth"
    />
    <slot v-else>
      <Square
        :size="size"
        :stroke-width="strokeWidth"
        :absolute-stroke-width="absoluteStrokeWidth"
      />
    </slot>
  </component>
</template>

<style scoped lang="scss">
.IconButton {
  @include reset-button;
  @include reset-link;
  @include flex-row-center;
  padding: 0px;
  cursor: pointer;
  transition: opacity .3s ease;
  transition: transform 200ms ease-out, opacity 200ms ease-out;

  &[active=true] {
    transform: scale(0.8);
    opacity: 0;
  }

  &[disabled=true] {
    opacity: 0.2;
    cursor: default;
  }
}
</style>
