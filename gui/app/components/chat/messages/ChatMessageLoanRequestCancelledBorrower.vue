<script setup lang="ts">
import { X } from 'lucide-vue-next'

const props = defineProps<{
  msg: ChatMessage
  me: User
}>()

// chat
const { me, msg } = toRefs(props)
</script>

<template>
  <ChatMessage
    :me="me"
    :msg="msg"
  >
    <X
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez annulé votre demande d'emprunt.</div>
  </ChatMessage>
</template>
