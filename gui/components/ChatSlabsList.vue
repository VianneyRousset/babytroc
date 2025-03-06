<script setup lang="ts">

const props = defineProps<{
  src: PaginatedSource<Chat>,
  target: string,
}>();

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

function getTargetRoute(chatId: string) {
  return router.resolve({ name: props.target, params: { chat_id: chatId } });
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

  <div ref="list" class="ChatSlabsList">

    <NuxtLink v-for="chat in props.src.data" :to="getTargetRoute(chat.id)">
      <ChatSlab :chat="chat" :key="`${chat.id}`" />
    </NuxtLink>

    <ListResultIndicator :end="props.src.end" :loading="src.status === 'pending'"
      :empty="src.status !== 'idle' && props.src.data.length === 0" :error="src.status === 'error'" class="container">
      <template v-slot:empty>Aucun message</template>
      <template v-slot:error>Une erreur est survenue.</template>
    </ListResultIndicator>

  </div>

</template>

<style scoped lang="scss">
.ChatSlabsList {
  @include flex-column;
  flex-grow: 1;
  overflow-y: scroll;
  align-items: stretch;

  a {
    @include reset-link;
    text-decoration: none;
  }

  .ChatSlab {
    border-bottom: 1px solid $neutral-200;
  }
}
</style>
