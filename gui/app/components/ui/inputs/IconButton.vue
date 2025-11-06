<script setup lang="ts">
import { Square, type LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(
  defineProps<{
    active?: boolean
    disabled?: boolean
    icon?: LucideIcon
    target?: string | RouteLocationGeneric
  }>(),
  {
    active: false,
    disabled: false,
  },
)

const { disabled, active, icon, target } = toRefs(props)
</script>

<template>
  <NuxtLink
    class="IconButton"
    role="button"
    :disabled="disabled"
    :active="active"
    :to="target"
  >
    <component
      :is="icon"
      v-if="icon"
      :size="32"
      :stroke-width="1.5"
    />
    <slot v-else>
      <Square
        :size="32"
        :stroke-width="1.5"
      />
    </slot>
  </NuxtLink>
</template>

<style scoped lang="scss">
a.IconButton {
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
