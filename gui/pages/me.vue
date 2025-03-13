<script setup lang="ts">

const { data, more } = usePaginatedFetch("/v1/items", {
});

</script>

<template>
  <div @click="more">
    Me
    {{ data }}
  </div>
</template>
