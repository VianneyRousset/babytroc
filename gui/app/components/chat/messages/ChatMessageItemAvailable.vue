<script setup lang="ts">
import { Check } from 'lucide-vue-next'

const props = defineProps<{
  message: ChatMessage
  me: UserPrivate
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
    <Check
      :size="24"
      :stroke-width="1.33"
    />
    <div>L'objet <b>{{ chat.item.name }}</b> est à nouveau disponible.</div>
  </ChatMessage>
</template>
