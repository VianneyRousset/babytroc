<script setup lang="ts">
import { X } from 'lucide-vue-next'

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
    <X
      :size="24"
      :stroke-width="1.33"
    />
    <div><b>{{ chat.owner.name }}</b> a refusé de vous prêter de l'objet <b>{{ chat.item.name }}</b></div>
  </ChatMessage>
</template>
