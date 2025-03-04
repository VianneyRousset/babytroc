import { ChatMessageType } from '#build/types/open-fetch/schemas/api';

const useChat = (chat: Ref<Chat | null>) => {

  const meStore = useMeStore();

  const isUserBorrowing: Ref<boolean | null> = computed(() => {

    if (chat.value === null || meStore.me === null)
      return null;

    return chat.value.borrower.id === meStore.me.id;

  });

  const interlocutor: Ref<UserPreview | null> = computed(() => {

    if (chat.value === null || isUserBorrowing.value === null)
      return null

    return isUserBorrowing.value ? chat.value.owner : chat.value.borrower;
  });

  const item: Ref<ItemPreview | null> = computed(() => chat.value?.item ?? null);

  return {
    isUserBorrowing,
    interlocutor,
    item,
  }
};

function useChatMessage(message: Ref<ChatMessage | null>) {

  const meStore = useMeStore();

  const messageType: Ref<ChatMessageType | null> = computed(() => message.value?.message_type ?? null);

  const source: Ref<"me" | "interlocutor" | "system" | null> = computed(() => {

    if (messageType.value === null)
      return null;

    if (messageType.value !== ChatMessageType.text)
      return "system";

    if (meStore.me === null)
      return null;

    return message.value!.sender_id === meStore.me.id ? "me" : "interlocutor"

  });

  return {
    id: message.value?.id ?? null,
    messageType,
    source,
    chatId: message.value?.chat_id ?? null,
    senderId: message.value?.sender_id ?? null,
    creationDate: message.value?.creation_date ?? null,
    seen: message.value?.seen ?? null,
    payload: message.value?.payload ?? null,
  }

}

export { useChat, useChatMessage };
