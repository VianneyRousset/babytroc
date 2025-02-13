<script setup lang="ts">

const props = withDefaults(defineProps<{

  // if false, the bar stays visible
  // if true, the bar is hidden when scrolling down
  // if an HTML element is given, the bar is hidden when the element is scolled down
  // default to false
  scroll?: boolean | HTMLElement,

  // min scroll y value to hide the bar
  // default to 0
  scrollOffset?: number,

}>(), {
  scroll: false,
  scrollOffset: 0,
});

// true scrolling down
const scrollingDown = ref(false);

// scroll y position
var y = ref(0);

// if a scrolling element is given, watch its scroll
// otherwise watch window scroll
if (props.scroll) {

  y = (props.scroll === true) ? useWindowScroll().y : useScroll(props.scroll).y;

  watch(y, (newY: number, oldY: number) => {
    scrollingDown.value = (newY > oldY);
  });
}

</script>

<template>
  <div :class="{ hidden: y > props.scrollOffset && scrollingDown }">
    <slot />
  </div>
</template>

<style scoped lang="scss">
div {

  @include flex-row;
  @include bar-shadow;
  gap: 16px;
  height: 64px;

  position: fixed;
  top: 0px;
  box-sizing: border-box;
  width: 100%;
  z-index: 5;

  transform: translate(0, 0);
  transition: 0.1s transform ease-out;

  padding: 0 1rem;

  background-color: $neutral-50;
  color: $neutral-700;
  border-bottom: 1px solid $neutral-300;

  &.hidden {
    transform: translate(0, -100%);
    box-shadow: none;
  }

  :deep(svg) {
    stroke: $neutral-700;
  }

  :deep(h1) {
    @include ellipsis-overflow;
    position: relative;
    top: -0.1rem;
    color: $neutral-700;
    flex-grow: 1;
    margin: 0;
    font-weight: 500;
    font-size: 1.6rem;
  }

}
</style>
