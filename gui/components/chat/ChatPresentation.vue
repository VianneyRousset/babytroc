<script setup lang="ts">
const props = defineProps<{
  me: User,
  chat: Chat,
}>();

const { me, chat } = toRefs(props);

// get messages
const { data: chatMessagesPages, loadMore: loadMoreMessages } = useChatMessagesListQuery(() => unref(chat).id);
const { data: meBorrowingsRequests } = useLoanRequestsQuery();
const { data: itemLoanRequests } = useItemLoanRequestsQuery(computed(() => unref(chat).item.id));

// mutations
const { mutate: sendMessage } = useSendMessageMutation();

// chat input
const chatMessageInput = ref("");

// is user the borrower or the owner ?
const { isUserBorrowing } = useChatRoles(chat, me);

// send message
async function submitMessage(msg: string) {
  await sendMessage({
    chatId: unref(chat).id,
    text: msg,
  });
  chatMessageInput.value = "";
}

</script>

<template>
  <div class="ChatPresentation">
    <ChatBorrowerMessagesList v-if="isUserBorrowing && meBorrowingsRequests" :messages="chatMessagesPages.data" :me="me"
      :chat="chat" :loan-requests="meBorrowingsRequests" />
    <ChatOwnerMessagesList v-else-if="!isUserBorrowing && itemLoanRequests" :messages="chatMessagesPages.data" :me="me"
      :chat="chat" :loan-requests="itemLoanRequests" />
    <ChatMessageInput v-model="chatMessageInput" @submit="submitMessage" />
  </div>
</template>

<style lang="scss" scoped>
.ChatMessageInput {
  position: absolute;
  bottom: 80px;
  left: 0;
  right: 0;
}
</style>
