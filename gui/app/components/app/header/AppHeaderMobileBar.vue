<script setup lang="ts">
const props = withDefaults(
	defineProps<{
		// if false, the bar stays visible
		// if true, the bar is hidden when scrolling down
		hideOnScroll?: HTMLElement | null;

		// min scroll y value to hide the bar
		// default to 0
		scrollOffset?: number;
	}>(),
	{},
);

const { hideOnScroll, scrollOffset } = toRefs(props);

// true if scrolling down
const scrollingDown = ref(false);
const scrolled = computed(() => unref(y) > 0);

// scroll y position
const { y } = useScroll(hideOnScroll);

watch(y, (newY: number, oldY: number) => {
	scrollingDown.value = newY > oldY;
});

// get header height and provide it to children elements
// if no header is present (e.g. in desktop mode), the height is 0
const { height: appHeaderBarHeight } = useElementSize(
	useTemplateRef("header"),
	undefined,
	{ box: "border-box" },
);
</script>

<template>
  <header
    ref="header"
    class="AppHeaderMobileBar"
    :class="{
      hidden: hideOnScroll && y > (scrollOffset ?? appHeaderBarHeight) && scrollingDown,
      scrolled: scrolled
    }"
  >
    <slot />
  </header>
</template>

<style scoped lang="scss">
.AppHeaderMobileBar {
  @include flex-row;
  gap: $space-4;
  height: 56px;

  transform: translate(0, 0);
  transition: transform 100ms ease-out, opacity 100ms ease-out, box-shadow 200ms ease-out;

  padding: 0 $space-4;

  background-color: $bg-surface;
  color: $text-primary;
  border-bottom: 1px solid $divider;

  box-shadow: none;

  &.scrolled {
    box-shadow: $shadow-sm;
  }

  &.hidden {
    transform: translate(0, -100%);
    opacity: 0;
    box-shadow: none;
  }

  :deep(& > svg) {
    stroke: $text-primary;
  }

  :deep(h1) {
    @include ellipsis-overflow;
    @include font-jakarta;
    position: relative;
    color: $text-primary;
    flex-grow: 1;
    margin: 0;
    font-weight: 600;
    font-size: 1.1rem;
    text-align: center;
  }
}
</style>
