<script setup lang="ts">
const props = defineProps<{
  me: User
  msg: ChatMessage
}>()

// chat
const { me, msg } = toRefs(props)
</script>

<template>
  <ChatMessage
    :me="me"
    :msg="msg"
  >
    {{ msg.text }}
  </ChatMessage>
</template>
