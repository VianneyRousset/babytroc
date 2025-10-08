<script setup lang="ts">
import { X } from 'lucide-vue-next'

const props = defineProps<{
  message: ChatMessage
  me: User
  chat: Chat
}>()

const { message, me } = toRefs(props)
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
    <div><b>{{ chat.borrower.name }}</b> a annulé sa demande.</div>
  </ChatMessage>
</template>
