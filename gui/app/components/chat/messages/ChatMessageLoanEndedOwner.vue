<script setup lang="ts">
import { LoanRequestState } from "#build/types/open-fetch/schemas/api";
import { Upload } from "lucide-vue-next";

const props = defineProps<{
	msg: ChatMessage;
	me: User;
	chat: Chat;
}>();

// chat
const { me, chat, msg } = toRefs(props);
</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <Upload :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div><b>{{ chat.borrower.name }}</b> vous rendu l'objet <b>{{ chat.item.name }}</b>.</div>
  </ChatMessage>
</template>
