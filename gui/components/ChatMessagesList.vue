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
    direction: "top",
  }
)

const { messageDateGroups } = useChatMessageList(computed(() => props.src.data));

watch(() => props.src.data, (newData) => {
  reset();
})

</script>

<template>

  <div ref="list" class="ChatMessagesList">

    <div v-for="dateGroup in messageDateGroups" :key="dateGroup.date" class="date-group">
      <div v-for="chunk in dateGroup.chunks" class="chunk" :key="chunk.key">
        <ChatMessage v-for="message in chunk.messages" :key="`chatMessage-${message.id}`" :message="message" />
      </div>
      <div class="date-bubble">
        {{ dateGroup.formattedDate }}
      </div>
    </div>

    <ListResultIndicator :end="props.src.end" :loading="src.status === 'pending'"
      :empty="src.status !== 'idle' && props.src.data.length === 0" :error="src.status === 'error'" class="container">
      <template v-slot:empty>Aucun message</template>
      <template v-slot:error>Une erreur est survenue.</template>
    </ListResultIndicator>

  </div>

</template>

<style scoped lang="scss">
.ChatMessagesList {
  gap: 1rem;
  @include flex-column;
  flex-direction: column-reverse;
  justify-content: flex-end;
  overflow-y: scroll;
  align-items: stretch;

  .date-group {
    @include flex-column;
    gap: 0.5rem;
    flex-direction: column-reverse;
    align-items: stretch;

    .date-bubble {
      align-self: center;

      background: $neutral-300;
      font-style: italic;
      padding: 0.3rem 1rem;
      border-radius: 9999px;
      color: white;
    }
  }

  .chunk {
    @include flex-column;
    align-items: stretch;

  }
}
</style>
