<script setup lang="ts">

const props = defineProps<{
  src: PaginatedSource<ChatMessage>,
}>();

const { reset } = useInfiniteScroll(
  useTemplateRef("list"),
  async () => {

    if (props.src.status == "pending" || props.src.end)
      return;

    await props.src.more();
  },
  {
    canLoadMore: () => !props.src.end,
    distance: 400,
  }
)

watch(() => props.src.data, (newData) => {
  reset();
})

</script>

<template>

  <div ref="list" class="ChatMessagesList">

    <ChatMessage v-for="message in props.src.data" :message="message" :key="`${message.id}`" />

    <ListResultIndicator :end="props.src.end" :loading="src.status === 'pending'"
      :empty="src.status !== 'idle' && props.src.data.length === 0" :error="src.status === 'error'" class="container">
      <template v-slot:empty>Aucun message</template>
      <template v-slot:error>Une erreur est survenue.</template>
    </ListResultIndicator>

  </div>

</template>

<style scoped lang="scss">
.ChatMessagesList {
  @include flex-column;
  flex-direction: column-reverse;
  justify-content: flex-end;
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
