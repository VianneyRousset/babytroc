<script setup lang="ts">

import { Square } from 'lucide-vue-next';

const props = withDefaults(defineProps<{
  disabled?: boolean,
}>(), {
  disabled: false,
});

</script>

<template>
  <div class="IconButton" role="button" :disabled="props.disabled">
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

  &[disabled=true] {
    opacity: 0.2;
    cursor: default;
  }
}
</style>
