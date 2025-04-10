<script setup lang="ts">
import VSwitch from '@lmiller1990/v-switch';
import { ChatMessageType } from '#build/types/open-fetch/schemas/api';

const props = defineProps<{
  me: User,
  chat: Chat,
  messages: Array<ChatMessage>,
}>();

const { me, chat, messages } = toRefs(props);

// group messages
const { dateGroups } = useGroupChatMessages(messages, me);

const { isUserBorrowing } = useChatRoles(chat, me);

</script>

<template>
  <List class="ChatMessagesList">
    <div v-for="dateGroup in dateGroups" :key="dateGroup.date" class="date-group">
      <div v-for="chunk in dateGroup.chunks" :key="chunk.key" class="chunk">
        <v-switch v-for="msg in chunk.messages" :key="`chatMessage-${msg.id}`" :case="msg.message_type">

          <template #[ChatMessageType.text]>
            <ChatMessageText :msg="msg" :me="me" />
          </template>

          <template #[ChatMessageType.loan_request_created]>
            <ChatMessageLoanRequestCreatedBorrower v-if="isUserBorrowing" :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
            <ChatMessageLoanRequestCreatedOwner v-else :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
          </template>

          <template #[ChatMessageType.loan_request_accepted]>
            <ChatMessageLoanRequestAcceptedBorrower v-if="isUserBorrowing" :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
            <ChatMessageLoanRequestAcceptedOwner v-else :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
          </template>

          <template #[ChatMessageType.loan_request_rejected]>
            <ChatMessageLoanRequestRejectedBorrower v-if="isUserBorrowing" :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
            <ChatMessageLoanRequestRejectedOwner v-else :msg="msg" :me="me" :chat="chat"
              :loan-request-id="msg.loan_request_id!" />
          </template>

          <template #[ChatMessageType.loan_started]>
            <ChatMessageLoanStartedBorrower v-if="isUserBorrowing" :msg="msg" :me="me" :chat="chat" />
            <ChatMessageLoanStartedOwner v-else :msg="msg" :me="me" :chat="chat" :loan-id="msg.loan_id!" />
          </template>

          <template #[ChatMessageType.loan_ended]>
            <ChatMessageLoanEndedBorrower v-if="isUserBorrowing" :msg="msg" :me="me" :chat="chat" />
            <ChatMessageLoanEndedOwner v-else :msg="msg" :me="me" :chat="chat" />
          </template>

          <template #[ChatMessageType.item_not_available]>
            <ChatMessageItemNotAvailable :msg="msg" :me="me" :chat="chat" />
          </template>

          <template #[ChatMessageType.item_available]>
            <ChatMessageItemAvailable :msg="msg" :me="me" :chat="chat" />
          </template>

        </v-switch>
      </div>

      <div class="date-bubble" :key="dateGroup.date">
        {{ dateGroup.formattedDate }}
      </div>

    </div>
  </List>
</template>

<style scoped lang="scss">
.ChatMessagesList {

  display: flex;
  flex-direction: column-reverse;
  align-items: stretch;
  gap: 1rem;

  .date-group {
    display: flex;
    flex-direction: column-reverse;

    align-items: stretch;
    gap: 0.5rem;

    .date-bubble {
      align-self: center;

      background: $neutral-300;
      font-style: italic;
      padding: 0.3rem 1rem;
      border-radius: 9999px;
      color: white;
    }
  }

  .chunk {
    display: flex;
    flex-direction: column-reverse;
    align-items: stretch;

  }
}
</style>
