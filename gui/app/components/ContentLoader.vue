<script setup lang="ts">
import { ContentLoader as CL } from 'vue-content-loader'
</script>

<template>
  <CL
    viewBox="0 0 1 1"
    :speed="4"
    primary-color="#f3f3f3"
    secondary-color="#ecebeb"
  >
    <slot />
  </CL>
</template>
