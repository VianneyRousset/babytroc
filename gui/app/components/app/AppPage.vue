<script setup lang="ts">
/**
 *
 *
 **/

const props = withDefaults(
  defineProps<{
    // if false, the bar stays visible
    // if true, the bar is hidden when scrolling down
    hideBarOnScroll?: boolean

    // min scroll y value to hide the bar
    // default to 0
    hideBarScrollOffset?: number

    // save the page scroll position with the given name
    savedScroll?: string

    // set infinite scroll to app page content
    infiniteScroll?: boolean

    // ininite scroll distance
    infiniteScrollDistance?: number

    // max width
    maxWidth?: number

    withHeader?: boolean
  }>(),
  {
    hideBarOnScroll: false,
    infiniteScroll: false,
    maxWidth: 1400,
    withHeader: false,
  },
)

const emit = defineEmits<{
  (event: 'more'): void
}>()

const { hideBarOnScroll, hideBarScrollOffset, savedScroll, infiniteScroll, infiniteScrollDistance, maxWidth } = toRefs(props)

const device = useDevice()

const slots = useSlots()

// get header bar height and provide it to children elements
// if no bar is present (e.g. in desktop mode), the height is 0
const { height: appHeaderBarHeight } = useElementSize(
  useTemplateRef('app-header-bar'),
  undefined,
  { box: 'border-box' },
)
provide('app-header-bar-height', appHeaderBarHeight)

// set infinite scroll
const page = useTemplateRef<HTMLDivElement>('page')
useInfiniteScroll(
  computed(() => unref(infiniteScroll) ? (device.isMobile ? unref(page) : document) : null),
  () => emit('more'),
  { distance: unref(infiniteScrollDistance) },
)
</script>

<template>
  <div
    ref="page"
    v-saved-scroll:[savedScroll]
    class="AppPage"
    :class="{ 'mobile': device.isMobile, 'with-header': withHeader }"
  >
    <!-- Header bar (mobile only) -->
    <AppHeaderMobileBar
      v-if="slots['mobile-header-bar'] && device.isMobile"
      ref="app-header-bar"
      :hide-on-scroll="hideBarOnScroll ? page : null"
      :scroll-offset="hideBarScrollOffset"
    >
      <slot name="mobile-header-bar" />
    </AppHeaderMobileBar>

    <!-- Left panel / drawer -->
    <aside
      v-if="slots['left']"
      class="left"
    >
      <slot name="left" />
    </aside>

    <slot
      v-if="device.isMobile"
      name="mobile"
    />
    <slot
      v-else
      name="desktop"
    />
    <slot />

    <!-- Right panel / drawer -->
    <aside
      v-if="slots['right']"
      class="right"
    >
      <slot name="right" />
    </aside>
  </div>
</template>

<style scoped lang="scss">
.AppPage {
  --app-header-bar-height: v-bind('appHeaderBarHeight + "px"');

  :deep(main) {
    @include flex-column;
    align-items: stretch;
  }

  &.mobile {
    position: fixed;
    width: 100%;
    height: 100%;
    background: white;
    overflow-y: scroll;

    :deep(main) {
      padding-top: var(--app-header-bar-height);
      padding-bottom: var(--app-footer-bar-height);
    }

    .AppHeaderMobileBar {
      position: fixed;
      top: 0;
      box-sizing: border-box;
      width: 100%;
      /* compensate for image gallery carousel z-index*/
      z-index: 2;
    }
  }

  &:not(.mobile) {
    display: grid;
    grid-template-columns: auto 1fr auto;
    grid-template-areas: "left main   right";

    width: 100%;
    max-width: v-bind("`${maxWidth}px`");

    &.with-header {
      grid-template-areas:
        ".    header ."
        "left main   right";
    }

    :deep(main) {
      grid-area: main;
      flex: 1;
    }

    :deep(header) {
      grid-area: header;
      flex: 0;
    }

    aside {
      &.left {
        grid-area: left;
      }
      &.right {
        grid-area: right;
      }
    }
  }
}
</style>
