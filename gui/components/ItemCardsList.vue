<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';

type Item = ApiResponse<'list_items_v1_items_get'>[number];

const props = defineProps<{
  src: PaginatedSource<Item>,
  target: string,
}>();

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

async function onClick(event: Event, itemId: number) {
  routeStack.amend(router.resolve({ ...route, hash: `#item${itemId}` }).fullPath);
}

function getTargetRoute(itemId: number) {
  return router.resolve({ name: props.target, params: { item_id: itemId } });
}

const { reset } = useInfiniteScroll(
  useTemplateRef("list"),
  async () => {

    if (props.src.status == "pending" || props.src.end)
      return;

    await props.src.more();
  },
  {
    canLoadMore: () => !props.src.end,
    distance: 1800,
  }
)

watch(() => props.src.data, (newData) => {
  reset();
})

</script>

<template>

  <div ref="list" class="list">

    <NuxtLink v-for="item in props.src.data" :to="getTargetRoute(item.id)"
      @click.native="event => onClick(event, item.id)" :key="item.id">
      <ItemCard :item="item" :id="`item${item.id}`" />
    </NuxtLink>

    <ListResultIndicator :end="props.src.end" :loading="src.status === 'pending'"
      :empty="src.status !== 'idle' && props.src.data.length === 0" :error="src.status === 'error'" class="container">
      <template v-slot:empty>Aucun résultat</template>
      <template v-slot:error>Une erreur est survenue.</template>
    </ListResultIndicator>

  </div>

</template>

<style scoped lang="scss">
.list {
  @include flex-column;
  flex-grow: 1;
  overflow-y: scroll;
  align-items: stretch;
  gap: var(--page-padding);
}

a {
  text-decoration: none;
}
</style>
