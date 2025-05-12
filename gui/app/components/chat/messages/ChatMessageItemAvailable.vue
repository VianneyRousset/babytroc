<script setup lang="ts">
import { Check } from 'lucide-vue-next'

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
    <Check
      :size="24"
      :stroke-width="1.33"
    />
    <div>L'objet <b>{{ chat.item.name }}</b> est à nouveau disponible.</div>
  </ChatMessage>
</template>
