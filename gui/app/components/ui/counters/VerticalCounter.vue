<script setup lang="ts">
const model = defineModel<number>()

const props = withDefaults(defineProps<{
  size?: 'large' | 'medium'
}>(), {
  size: 'medium',
})

const { size } = toRefs(props)
</script>

<template>
  <div class="VerticalCounter">
    <div>{{ model ?? '...' }}</div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.VerticalCounter {
  @include flex-column;
  justify-content: center;
  gap: 0.6em;

  color: $neutral-700;
  min-width: v-bind("size === 'large' ? '8em' : '4em'");

  & > *:last-child {
    @include font-inter;
    font-size: v-bind("size === 'large' ? '4em' : '2em'");
  }

  & > *:last-child {
    @include font-jakarta;
  }
}
</style>
