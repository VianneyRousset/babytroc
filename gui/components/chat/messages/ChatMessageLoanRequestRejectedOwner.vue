<script setup lang="ts">
import { LoanRequestState } from '#build/types/open-fetch/schemas/api';
import { CircleOff } from 'lucide-vue-next';

const props = defineProps<{
  msg: ChatMessage,
  me: User,
  chat: Chat,
  loanRequestId: number,
}>();

</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <CircleOff :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div>Vous avez refusé le prêt.</div>
  </ChatMessage>
</template>
