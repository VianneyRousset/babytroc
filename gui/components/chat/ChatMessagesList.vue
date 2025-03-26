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

</script>

<template>
  <List class="ChatMessagesList">
    <div v-for="dateGroup in dateGroups" :key="dateGroup.date" class="date-group">
      <div v-for="chunk in dateGroup.chunks" :key="chunk.key" class="chunk">
        <ChatMessage v-for="msg in chunk.messages" :key="`chatMessage-${msg.id}`" :me="me" :msg="msg">
          <v-switch :case="msg.message_type">

            <template #[ChatMessageType.text] :msg="msg">
              <slot name="text" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_request_created] :msg="msg">
              <slot name="loan-request-created" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_request_cancelled] :msg="msg">
              <slot name="loan-request-cancelled" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_request_accepted] :msg="msg">
              <slot name="loan-request-accepted" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_request_rejected] :msg="msg">
              <slot name="loan-request-rejected" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_started] :msg="msg">
              <slot name="loan-started" :msg="msg" />
            </template>

            <template #[ChatMessageType.loan_ended] :msg="msg">
              <slot name="loan-ended" :msg="msg" />
            </template>

            <template #[ChatMessageType.item_not_available] :msg="msg">
              <slot name="item-not-available" :msg="msg" />
            </template>

            <template #[ChatMessageType.item_available] :msg="msg">
              <slot name="item-available" :msg="msg" />
            </template>

          </v-switch>
        </ChatMessage>
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
