<script setup lang="ts">
const props = defineProps<{
  me: User,
  chat: Chat,
}>();

const { me, chat } = toRefs(props);

// get messages
const { data: chatMessagesPages, loadMore: loadMoreMessages } = useChatMessagesListQuery(() => unref(chat).id);

// mutations
const { mutate: sendMessage } = useSendMessageMutation();

// chat input
const inputeText = ref("");

// send message
async function submitMessage(msg: string) {
  await sendMessage({
    chatId: unref(chat).id,
    text: msg,
  });
  inputeText.value = "";
}

const chatMessageInput = useTemplateRef<HTMLElement>("chat-message-input");
const { height: chatMessageInputHeight } = useElementSize(chatMessageInput, undefined, { box: "border-box" });

</script>

<template>
  <div class="ChatPresentation">
    <ChatMessagesList :me="me" :chat="chat" :messages="chatMessagesPages.data" />
    <ChatMessageInput ref="chat-message-input" v-model="inputeText" @submit="submitMessage" />
  </div>
</template>

<style lang="scss" scoped>
.ChatPresentation {

  --chat-message-input-height: v-bind(chatMessageInputHeight + "px");

  padding-top: calc(var(--footer-height) + 1rem);
  padding-bottom: calc(var(--footer-height) + var(--chat-message-input-height) + 1rem);

  .ChatMessageInput {
    position: absolute;
    bottom: calc(var(--footer-height) + 1rem);
    left: 0;
    right: 0;
  }
}
</style>
