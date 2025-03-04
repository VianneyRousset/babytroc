<script setup lang="ts">

const props = defineProps<{
  message: ChatMessage,
}>();

// chat
const { message } = toRefs(props);
const { source, payload } = useChatMessage(message);

</script>

<template>
  <div class="ChatMessage">
    {{ payload }}
  </div>
</template>

<style scoped lang="scss">
.ChatMessage {
  border: 1px solid gray;

}
</style>
