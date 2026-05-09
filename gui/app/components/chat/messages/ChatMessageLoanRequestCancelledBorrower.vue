<script setup lang="ts">
const props = defineProps<{
	message: ChatMessage;
	me: UserPrivate;
}>();

// chat
const { me, message } = toRefs(props);
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
    <div>Vous avez annulé votre demande d'emprunt.</div>
  </ChatMessage>
</template>
