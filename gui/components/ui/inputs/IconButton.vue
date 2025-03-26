<script setup lang="ts">

import { Square } from 'lucide-vue-next';

const props = withDefaults(defineProps<{
  active?: boolean,
  disabled?: boolean,
}>(), {
  active: false,
  disabled: false,
});

const { disabled, active } = toRefs(props);

</script>

<template>
  <div class="IconButton" role="button" :disabled="disabled" :active="active">
    <slot>
      <Square :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
    </slot>
  </div>
</template>

<style scoped lang="scss">
.IconButton {
  @include reset-button;
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
