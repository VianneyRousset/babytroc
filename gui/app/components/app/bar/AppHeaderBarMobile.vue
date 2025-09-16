<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    // if false, the bar stays visible
    // if true, the bar is hidden when scrolling down
    hideOnScroll?: HTMLElement | null

    // min scroll y value to hide the bar
    // default to 0
    scrollOffset?: number
  }>(),
  { },
)

const { hideOnScroll, scrollOffset } = toRefs(props)

// true if scrolling down
const scrollingDown = ref(false)

// scroll y position
const { y } = useScroll(hideOnScroll)

watch(y, (newY: number, oldY: number) => {
  scrollingDown.value = newY > oldY
})

// get header height and provide it to children elements
// if no header is present (e.g. in desktop mode), the height is 0
const { height: appHeaderBarHeight } = useElementSize(
  useTemplateRef('header'),
  undefined,
  { box: 'border-box' },
)
</script>

<template>
  <div
    ref="header"
    class="AppHeaderBarMobile"
    :class="{ hidden: hideOnScroll && y > (scrollOffset ?? appHeaderBarHeight) && scrollingDown }"
  >
    <slot />
  </div>
</template>

<style scoped lang="scss">
.AppHeaderBarMobile {

  @include flex-row;
  @include bar-shadow;
  gap: 16px;
  height: 64px;

  transform: translate(0, 0);
  transition: 0.1s transform ease-out, 0.1s opacity ease-out;

  padding: 0 1rem;

  background-color: $neutral-50;
  color: $neutral-700;
  border-bottom: 1px solid $neutral-300;

  &.hidden {
    transform: translate(0, -100%);
    opacity: 0;
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
