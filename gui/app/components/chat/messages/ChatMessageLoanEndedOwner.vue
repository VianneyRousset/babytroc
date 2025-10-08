<script setup lang="ts">
import { Upload } from 'lucide-vue-next'

const props = defineProps<{
  message: ChatMessage
  me: User
  chat: Chat
}>()

// chat
const { me, chat, message } = toRefs(props)
</script>

<template>
  <ChatMessage
    :me="me"
    :message="message"
  >
    <Upload
      :size="24"
      :stroke-width="1.33"
    />
    <div><b>{{ chat.borrower.name }}</b> vous rendu l'objet <b>{{ chat.item.name }}</b>.</div>
  </ChatMessage>
</template>
