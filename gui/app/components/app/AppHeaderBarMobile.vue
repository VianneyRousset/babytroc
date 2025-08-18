<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    // if false, the bar stays visible
    // if true, the bar is hidden when scrolling down
    // if an HTML element is given, the bar is hidden when the element is scolled down
    // default to false
    scroll?: HTMLElement | boolean

    // min scroll y value to hide the bar
    // default to 0
    scrollOffset?: number
  }>(),
  {
    scroll: false,
    scrollOffset: 0,
  },
)

const { scroll, scrollOffset } = toRefs(props)

// true if scrolling down
const scrollingDown = ref(false)

const scrollElement = computed(() => {
  const _scroll = unref(scroll)
  return _scroll === false ? undefined : (_scroll === true ? window : _scroll)
})

// scroll y position
const { y } = useScroll(scrollElement)

watch(y, (newY: number, oldY: number) => {
  scrollingDown.value = newY > oldY
})
</script>

<template>
  <div
    class="AppHeaderBar"
    :class="{ hidden: y > scrollOffset && scrollingDown }"
  >
    <slot />
  </div>
</template>

<style scoped lang="scss">
.AppHeaderBar {

  @include flex-row;
  @include bar-shadow;
  gap: 16px;
  height: 64px;

  position: sticky;
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

  :deep(&>svg) {
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
