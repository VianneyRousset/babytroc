<script setup lang="ts">
import { Upload } from 'lucide-vue-next'

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
    <Upload
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez rendu l'objet <b>{{ chat.item.name }}.</b></div>
  </ChatMessage>
</template>
