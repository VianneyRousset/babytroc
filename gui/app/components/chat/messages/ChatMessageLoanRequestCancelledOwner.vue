<script setup lang="ts">
const props = defineProps<{
	message: ChatMessage;
	me: UserPrivate;
	chat: Chat;
}>();

const { message, me } = toRefs(props);
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
