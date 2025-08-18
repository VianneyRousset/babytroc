<script setup lang="ts">
const device = useDevice()

// get footer height and provide it to children elements
// if no footer is present (e.g. in desktop mode), the height is 0
const { height: appFooterHeight } = useElementSize(
  useTemplateRef('footer'),
  undefined,
  { box: 'border-box' },
)
provide('appFooterHeight', appFooterHeight)
</script>

<template>
  <div class="layout">
    <AppNavigationDesktop v-if="!device.isMobile" />
    <slot />
    <AppNavigationMobile
      v-if="device.isMobile"
      ref="footer"
    />
  </div>
</template>

<style lang="scss" scoped>
.layout {
  --app-footer-height: v-bind('appFooterHeight + "px"');
  margin-bottom: var(--app-footer-height);
}
</style>
