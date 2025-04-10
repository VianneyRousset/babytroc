<script setup lang="ts">
import { LoanRequestState } from '#build/types/open-fetch/schemas/api';
import { Check } from 'lucide-vue-next';

const props = defineProps<{
  msg: ChatMessage,
  me: User,
  chat: Chat,
}>();

// chat
const { me, chat, msg } = toRefs(props);

</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <Check :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div>L'objet <b>{{ chat.item.name }}</b> est à nouveau disponible.</div>
  </ChatMessage>
</template>
