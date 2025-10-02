<script setup lang="ts">
import { Square } from 'lucide-vue-next'

const model = defineModel<boolean>()

const props = withDefaults(
  defineProps<{
    active?: boolean
    disabled?: boolean
  }>(),
  {
    active: false,
    disabled: false,
  },
)

const { disabled, active } = toRefs(props)
</script>

<template>
  <div
    class="ToggleIcon"
    role="button"
    :disabled="disabled"
    :active="active"
    @click="model = !model"
  >
    <slot>
      <Square
        :size="24"
        :stroke-width="2"
      />
    </slot>
  </div>
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
