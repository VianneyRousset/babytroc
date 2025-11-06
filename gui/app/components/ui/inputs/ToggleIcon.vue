<script setup lang="ts">
import { Square, type LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const model = defineModel<boolean>()

export type ToggleIconProps = {
  active?: boolean
  disabled?: boolean
  icon?: LucideIcon
  target?: string | RouteLocationGeneric
}

const props = withDefaults(
  defineProps<ToggleIconProps>(),
  {
    active: false,
    disabled: false,
  },
)

const { disabled, active, icon, target } = toRefs(props)
</script>

<template>
  <NuxtLink
    class="ToggleIcon"
    role="button"
    :disabled="disabled"
    :active="active"
    :to="target"
    @click="model = !model"
  >
    <component
      :is="icon"
      v-if="icon"
      :size="24"
      :stroke-width="2"
    />
    <slot v-else>
      <Square
        :size="24"
        :stroke-width="2"
      />
    </slot>
  </NuxtLink>
</template>

<style scoped lang="scss">
.ToggleIcon {

  @include reset-button;
  @include flex-column-center;

  padding: 0.5em;

  cursor: pointer;

  &[active=true] {
    :deep(svg) {
      stroke: $primary-400;
    }
  }

  &[disabled=true] {
    cursor: default;
  }
}
</style>
