<script setup lang="ts">

import { ContentLoader as CL } from "vue-content-loader";

</script>

<template>
  <CL viewBox="0 0 1 1" :speed="4" primaryColor="#f3f3f3" secondaryColor="#ecebeb">
    <slot />
  </CL>
</template>
