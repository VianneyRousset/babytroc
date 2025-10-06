<script setup lang="ts">
import { Circle } from 'lucide-vue-next'

const model = defineModel<number>()

const props = defineProps<{
  size?: 'normal' | 'small' | 'tiny'
}>()

const symbolSize = computed(() => {
  switch (props.size ?? 'normal') {
    case 'normal':
      return 32
    case 'small':
      return 24
    case 'tiny':
      return 16
    default:
      throw new Error(`Unhandled case: ${props.size}`)
  }
})

const symbolStrokeWidth = computed(() => {
  switch (props.size ?? 'normal') {
    case 'normal':
      return 2
    case 'small':
      return 2
    case 'tiny':
      return 1.2
    default:
      throw new Error(`Unhandled case: ${props.size}`)
  }
})
</script>

<template>
  <div
    class="HorizontalCounter"
    :class="{ small: props.size === 'small', tiny: props.size === 'tiny' }"
  >
    <slot>
      <Circle
        :size="symbolSize"
        :stroke-width="symbolStrokeWidth"
      />
    </slot>
    <div>{{ model ?? '...' }}</div>
  </div>
</template>

<style scoped lang="scss">
.HorizontalCounter {
  @include flex-row;
  justify-content: center;
  margin: 0.8rem 1.2rem;
  gap: 0.6rem;

  font-family: "Inter", sans-serif;
  font-size: 1.5rem;
  color: $neutral-700;

  &.small {
    gap: 0.4rem;
    font-size: 1rem;
    margin: 0.4rem 0.6rem;
  }

  &.tiny {
    gap: 0.2rem;
    font-size: 12px;
    margin: 0.2rem 0.4rem;
  }

  :deep(svg.filled) {
    fill: $neutral-700;
  }

  div:last-child {
    margin: 0px;
  }
}
</style>
