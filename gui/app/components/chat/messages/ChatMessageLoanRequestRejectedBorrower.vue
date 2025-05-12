<script setup lang="ts">
import { CircleOff } from 'lucide-vue-next'

const props = defineProps<{
  msg: ChatMessage
  me: User
  chat: Chat
}>()

// chat
const { me, chat, msg } = toRefs(props)
</script>

<template>
  <ChatMessage
    :me="me"
    :msg="msg"
  >
    <CircleOff
      :size="24"
      :stroke-width="1.33"
    />
    <div><b>{{ chat.owner.name }}</b> a refusé de vous prêter de l'objet <b>{{ chat.item.name }}</b></div>
  </ChatMessage>
</template>
