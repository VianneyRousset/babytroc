<script setup lang="ts">
// const footprintLeft = defineModel<number>('footprint-left')
// const footprintRight = defineModel<number>('footprint-right')
// const footprintTop = defineModel<number>('footprint-top')
// const footprintBottom = defineModel<number>('footprint-bottom')

const container = useTemplateRef<HTMLElement>('container')
const floating = useTemplateRef<HTMLElement>('floating')

const { bottom: containerBottom } = useElementBounding(container)
const { y: floatingTop } = useElementBounding(floating)

const footprintBottom = computed(() => unref(containerBottom) - unref(floatingTop))
</script>

<template>
  <div
    ref="container"
    class="WithFloating"
  >
    <slot />
    <div
      ref="floating"
      class="floating"
    >
      <slot name="floating" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.WithFloating {
  position: relative;

  .floating {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
  }

  :slotted(.with-floating-padding) {
    padding-bottom: v-bind("`${footprintBottom}px`");
  }
}
</style>
