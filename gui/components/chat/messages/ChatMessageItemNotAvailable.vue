<script setup lang="ts">
import { Clock } from 'lucide-vue-next';

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
    <Clock :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div>L'objet <b>{{ chat.item.name }}</b> n'est plus disponible.</div>
  </ChatMessage>
</template>
