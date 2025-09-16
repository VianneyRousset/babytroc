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
  }>(),
  {
    hideBarOnScroll: false,
    infiniteScroll: false,
  },
)

const emit = defineEmits<{
  (event: 'more'): void
}>()

const { hideBarOnScroll, hideBarScrollOffset, savedScroll, infiniteScroll, infiniteScrollDistance } = toRefs(props)

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
  <!-- Mobile page -->
  <div
    ref="page"
    :class="{ AppPage: true, mobile: device.isMobile }"
  >
    <!-- Header bar (mobile only) -->
    <header v-if="slots['mobile-header-bar'] && device.isMobile">
      <AppHeaderBarMobile
        ref="app-header-bar"
        :hide-on-scroll="hideBarOnScroll ? page : null"
        :scroll-offset="hideBarScrollOffset"
      >
        <slot name="mobile-header-bar" />
      </AppHeaderBarMobile>
    </header>

    <!-- Page header (desktop/tablet only) -->
    <header v-if="slots['desktop-header'] && !device.isMobile">
      <slot name="desktop-header" />
    </header>

    <!-- Left panel / drawer -->
    <aside
      v-if="slots['left']"
      class="left"
    >
      <slot name="left" />
    </aside>

    <!-- Main content -->
    <main
      ref="main"
      v-saved-scroll:[savedScroll]
    >
      <slot />
    </main>

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
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-areas:
    ". header ."
    "left main right";
  width: 100%;
  max-width: 1400px;

  header {
    grid-area: header;
    @include flex-column;
    align-items: stretch;
    justify-content: center;
  }

  aside {
    &.left {
      grid-area: left;
    }
    &.right {
      grid-area: right;
    }
  }

  main {
    grid-area: main;

    @include flex-column;
    align-items: stretch;
    flex: 1;
  }

  &.mobile {
    position: fixed;
    width: 100%;
    height: 100%;

    @include flex-column;
    align-items: stretch;

    background: white;
    overflow-y: scroll;

    main {
      padding-top: var(--app-header-bar-height);
      padding-bottom: var(--app-footer-bar-height);
    }
  }

  .AppHeaderBarMobile {
    position: fixed;
    top: 0;
    box-sizing: border-box;
    width: 100%;
  }
}
</style>
