<script setup lang="ts">
const props = defineProps<{
  active?: string
}>()

const { active } = toRefs(props)

const { me } = useMe()
const { chats, isLoading, loadMore, end } = useChats()

const scroller = useTemplateRef<HTMLElement>('scroller')

useInfiniteScroll(
  scroller,
  loadMore,
  {
    canLoadMore: () => !unref(end),
    distance: 300,
  },
)
</script>

<template>
  <SlabList
    v-if="me && chats"
    ref="scroller"
    class="ChatsList"
  >
    <ChatSlab
      v-for="chat in chats"
      :id="`chat-${chat.id}`"
      :key="`chat-${chat.id}`"
      :target="`/chats/${chat.id}`"
      class="reset-link"
      :chat="chat"
      :me="me"
      :class="{ active: active != null && active == chat.id, inactive: active != null && active != chat.id }"
    />
    <ListEmpty v-if="chats.length === 0">
      Vous n'avez pas encore de message.
    </ListEmpty>
    <LoadingAnimation v-if="isLoading" />
  </SlabList>
</template>

<style scoped lang="scss">
.SlabList {

  overflow-y: scroll;
  scrollbar-width: none;

  .active {
    background: $primary-50;
  }

  .LoadingAnimation {
    padding: 2em 0;
  }
}
</style>
