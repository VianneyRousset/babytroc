<script setup lang="ts">
const props = defineProps<{
  me: UserPrivate
  message: ChatMessage
}>()

// chat
const { me, message } = toRefs(props)
</script>

<template>
  <ChatMessage
    :me="me"
    :message="message"
  >
    {{ message.text }}
  </ChatMessage>
</template>
