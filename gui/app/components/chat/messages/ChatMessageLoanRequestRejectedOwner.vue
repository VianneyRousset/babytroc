<script setup lang="ts">
import { X } from 'lucide-vue-next'

const props = defineProps<{
  message: ChatMessage
  me: User
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
    <div>Vous avez refusé le prêt.</div>
  </ChatMessage>
</template>
