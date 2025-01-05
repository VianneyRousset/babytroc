<script setup lang="ts">
import { useWindowScroll } from '@vueuse/core'

const { x, y } = useWindowScroll();
const scrollingDown = ref(false);

watch(y, (newY, oldY) => {
  scrollingDown.value = (newY > oldY);
});

</script>

<template>
  <div :class="{ hidden: y > 0 && scrollingDown }">
    <slot />
  </div>
</template>

<style scoped lang="scss">
div {

  @include bar-shadow;

  position: fixed;
  top: 0px;
  box-sizing: border-box;
  width: 100%;

  transform: translate3d(0, 0, 0);
  transition: 0.1s all ease-out;

  padding: 0px 18px;

  background-color: $neutral-50;
  color: $neutral-500;
  border-bottom: 1px solid $neutral-300;
  font-family: 'Plus Jakarta Sans', serif;


  svg {
    stroke: $neutral-500;
  }

  input {
    font-family: inherit;
  }

  &.hidden {
    transform: translate3d(0, -100%, 0);
    box-shadow: none;
  }
}
</style>
