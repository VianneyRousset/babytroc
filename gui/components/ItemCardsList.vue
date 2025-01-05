<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';

type ItemList = ApiResponse<'list_items_v1_items_get'>

const props = defineProps<{
  items: ItemList | null
}>();


</script>

<template>

  <div class="list">
    <ItemCard v-for="item in props.items" v-if="props.items !== null" :item="item" />
  </div>

</template>

<style scoped lang="scss">
.list {
  display: flex;
  flex-direction: column;
  gap: 1em;
  padding: 1em;
}
</style>
