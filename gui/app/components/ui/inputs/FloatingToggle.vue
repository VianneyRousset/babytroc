<script setup lang="ts">
import type { ToggleIconProps } from './ToggleIcon.vue'

const model = defineModel<boolean>()

const props = defineProps<ToggleIconProps>()
</script>

<template>
  <ToggleIcon
    v-bind="props"
    v-model="model"
    class="FloatingToggle"
  >
    <slot />
  </ToggleIcon>
</template>

<style scoped lang="scss">
.FloatingToggle {

  @include bar-shadow;
  @include flex-column-center;

  padding: 0.75em;
  background: $neutral-50;
  border-radius: 50%;

  color: $neutral-700;

  cursor: pointer;

  &:hover {
    background: $neutral-200;
  }

  &:active {
    transform: scale(0.9);
  }

  &[active=true] {
    color: $primary-800;
  }

  &[disabled=true] {
    cursor: default;
  }
}
</style>
