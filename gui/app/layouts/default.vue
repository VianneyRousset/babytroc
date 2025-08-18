<script setup lang="ts">
const device = useDevice()
</script>

<template>
  <div>
    <AppNavigationMobile v-if="device.isMobile" />
    <AppNavigationDesktop v-else />
    <slot />
  </div>
</template>
