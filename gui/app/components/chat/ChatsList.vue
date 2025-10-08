<script setup lang="ts">
const { me } = useMe()
const { chats } = useChats()
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
      />
      <!-- TODO add empty -->
    </NuxtLink>
    <ListEmpty v-if="chats.length === 0">
      Vous n'avez pas encore de message.
    </ListEmpty>
  </SlabList>
</template>

<style scoped lang="scss">
</style>
