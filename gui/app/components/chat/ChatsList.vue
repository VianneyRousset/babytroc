<script setup lang="ts">
const props = defineProps<{
  active?: string
}>()

const { active } = toRefs(props)

const { me } = useMe()
const { chats, loadMore } = useChats()

loadMore()
</script>

<template>
  <SlabList
    v-if="me && chats"
    class="ChatsList"
  >
    <NuxtLink
      v-for="chat in chats"
      :id="`chat-${chat.id}`"
      :key="`chat-${chat.id}`"
      :to="`/chats/${chat.id}`"
      class="reset-link"
    >
      <ChatSlab
        :key="`${chat.id}`"
        :chat="chat"
        :me="me"
        :class="{ active: active != null && active == chat.id, inactive: active != null && active != chat.id }"
      />
      <!-- TODO add empty -->
    </NuxtLink>
    <ListEmpty v-if="chats.length === 0">
      Vous n'avez pas encore de message.
    </ListEmpty>
  </SlabList>
</template>

<style scoped lang="scss">
.active {
  background: $primary-50;
}
</style>
