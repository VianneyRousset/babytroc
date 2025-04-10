<script setup lang="ts">

import { MessageCircleQuestion, CircleDashed, PartyPopper, Heart, CircleStop, Clock, Check } from 'lucide-vue-next';

const props = defineProps<{
  me: User,
  msg: ChatMessage,
}>();

// chat
const { me, msg } = toRefs(props);
</script>

<template>
  <ChatMessage :me="me" :msg="msg">{{ msg.text }}</ChatMessage>
</template>
