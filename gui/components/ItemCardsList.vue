<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';

type ItemList = ApiResponse<'list_items_v1_items_get'>

const props = defineProps<{
  items: ItemList,
  target: string,
}>();

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

async function onClick(event: Event, itemId: number) {
  routeStack.amend(router.resolve({ path: route.path, hash: `#item${itemId}` }).fullPath);
}

function getTargetRoute(itemId: number) {
  return router.resolve({ name: props.target, params: { item_id: itemId } });
}

</script>

<template>

  <div class="list">
    <NuxtLink v-for="item in props.items" v-if="props.items !== null" :to="getTargetRoute(item.id)"
      @click.native="event => onClick(event, item.id)">
      <ItemCard :item="item" :id="`item${item.id}`" />
    </NuxtLink>
  </div>

</template>

<style scoped lang="scss">
.list {
  display: flex;
  flex-direction: column;
  gap: 1em;
  padding: 1em;

  * {
    text-decoration: none;
  }

}
</style>
