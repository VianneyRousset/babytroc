<script setup lang="ts">
import type { LucideIcon } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  icon?: LucideIcon
  color?: 'neutral' | 'primary' | 'red'
}>(), {
  color: 'neutral',
})

const { icon } = toRefs(props)
const slots = useSlots()
</script>

<template>
  <div
    class="PanelBanner"
    :class="[color]"
  >
    <slot name="icon">
      <component
        :is="icon"
        v-if="icon"
        :size="64"
        :stroke-width="1.33"
      />
    </slot>
    <div v-if="slots.default">
      <slot />
    </div>
  </div>
</template>

<style scoped lang="scss">
.PanelBanner {
  @include flex-column-center;
  gap: 2rem;
  padding: 4rem 0;
  color: $neutral-600;

  &.primary {
    color: $primary-400;
  }

  &.red {
    color: $red-800;
  }
}
</style>
