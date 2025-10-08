<script setup lang="ts">
import { Import } from 'lucide-vue-next'

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
    <Import
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez reçu l'objet <b>{{ chat.item.name }}.</b></div>
  </ChatMessage>
</template>
