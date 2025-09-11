<script setup lang="ts">
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

const emit = defineEmits(['more'])

const { hideBarOnScroll, hideBarScrollOffset, savedScroll, infiniteScroll, infiniteScrollDistance } = toRefs(props)

const device = useDevice()

// get header bar height and provide it to children elements
// if no bar is present (e.g. in desktop mode), the height is 0
const { height: appHeaderBarHeight } = useElementSize(
  useTemplateRef('app-header-bar'),
  undefined,
  { box: 'border-box' },
)
provide('app-header-bar-height', appHeaderBarHeight)

// set infinite scroll
const appPageContent = useTemplateRef<HTMLDivElement>('app-page-content')
useInfiniteScroll(
  computed(() => unref(infiniteScroll) ? unref(appPageContent) : null),
  () => emit('more'),
  { distance: unref(infiniteScrollDistance) },
)
</script>

<template>
  <div
    class="AppPage"
    :class="{ fixed: device.isMobileOrTablet }"
  >
    <!-- Header bar -->
    <AppHeaderBarMobile
      v-if="device.isMobileOrTablet"
      ref="app-header-bar"
      :hide-on-scroll="hideBarOnScroll ? appPageContent : null"
      :scroll-offset="hideBarScrollOffset"
    >
      <slot name="header" />
    </AppHeaderBarMobile>
    <div
      ref="app-page-content"
      v-saved-scroll:[savedScroll]
      class="app-page-content"
    >
      <div>
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.AppPage {
  --app-header-bar-height: v-bind('appHeaderBarHeight + "px"');

  &.fixed {
    position: fixed;
    width: 100%;
    height: 100%;
    background: white;

    .app-page-content {
      overflow-y: scroll;
      height: 100%;
      & > div {
        padding-top: var(--app-header-bar-height);
        padding-bottom: var(--app-footer-bar-height);
      }
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
