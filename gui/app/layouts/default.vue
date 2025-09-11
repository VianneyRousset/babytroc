<script setup lang="ts">
const device = useDevice()

// get footer bar height and provide it to children elements
// if no bar is present (e.g. in desktop mode), the height is 0
const { height: appFooterBarHeight } = useElementSize(
  useTemplateRef('app-footer-bar'),
  undefined,
  { box: 'border-box' },
)

provide('app-footer-bar-height', appFooterBarHeight)
</script>

<template>
  <div class="layout">
    <AppNavigationDesktop v-if="!device.isMobileOrTablet" />
    <slot />
    <AppNavigationMobile
      v-if="device.isMobileOrTablet"
      ref="app-footer-bar"
    />
  </div>
</template>

<style lang="scss" scoped>
.layout {
  --app-footer-bar-height: v-bind('appFooterBarHeight + "px"');
}
</style>
