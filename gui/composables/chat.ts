import { ChatMessageType } from '#build/types/open-fetch/schemas/api';
import { DateTime } from "luxon";

function getChatMessageOrigin(message: ChatMessage, meId: number): ChatMessageOrigin {

  if (message.message_type !== ChatMessageType.text)
    return "system";

  return message.sender_id === meId ? "me" : "interlocutor"
}

function formatRelativeDate(dt: DateTime) {

  const now = DateTime.local();

  if (dt.hasSame(now, "day"))
    return "Aujourd'hui";

  if (dt.hasSame(now.minus({ days: 1 }), "day"))
    return "Hier";

  if (dt.hasSame(now, "year"))
    return dt.toLocaleString({ month: "long", day: "numeric" });

  return dt.toFormat("DDD");
}




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

  const origin: Ref<ChatMessageOrigin | null> = computed(() => {

    if (messageType.value === null)
      return null;

    if (messageType.value !== ChatMessageType.text)
      return "system";

    if (meStore.me === null)
      return null;

    return message.value!.sender_id === meStore.me.id ? "me" : "interlocutor"

  });

  const text: Ref<string | null> = computed(() => {

    if (message.value === null || messageType.value === null)
      return null;

    switch (messageType.value) {
      case ChatMessageType.text:
        return message.value!.payload;
      case ChatMessageType.loan_request_created:
        return "Demande de prêt envoyée"
      case ChatMessageType.loan_request_canceled:
      case ChatMessageType.loan_request_accepted:
      case ChatMessageType.loan_request_rejected:
      case ChatMessageType.loan_started:
      case ChatMessageType.loan_ended:
      case ChatMessageType.item_not_available:
      case ChatMessageType.item_available:
    }

    return null
  });

  const formattedHour: Ref<string | null> = computed(() => {

    if (message.value === null)
      return null;

    return DateTime.fromISO(message.value!.creation_date).toLocaleString(DateTime.TIME_SIMPLE);
  })

  return {
    id: message.value?.id ?? null,
    messageType,
    origin,
    text,
    chatId: message.value?.chat_id ?? null,
    senderId: message.value?.sender_id ?? null,
    creationDate: message.value?.creation_date ?? null,
    seen: message.value?.seen ?? null,
    payload: message.value?.payload ?? null,
    formattedHour,
  }

}

function useChatMessageList(messages: Ref<Array<ChatMessage>>) {

  const meStore = useMeStore();

  function groupByMessageDateGroups(messages: Array<ChatMessage>, meId: number): Array<ChatMessageDateGroup> {

    // group message by creation date
    const groups = Object.groupBy(messages, ({ creation_date }) => DateTime.fromISO(creation_date).toISODate() ?? "") as Record<string, Array<ChatMessage>>;

    // sort groups by min message id and convert into chunks
    return Object.entries(groups)
      .sort(([_a, a], [_b, b]) => Math.min.apply(b.map((msg) => msg.id)) - Math.min.apply(a.map((msg) => msg.id)))
      .map(([date, messages]) => createMessageDateGroup(date, messages, meId));
  }

  function createMessageDateGroup(date: string, messages: Array<ChatMessage>, meId: number): ChatMessageDateGroup {
    return {
      date,
      formattedDate: formatRelativeDate(DateTime.fromISO(date)),
      chunks: groupByMessageChunks(messages.sort((a, b) => b.id - a.id), meId),
    }
  }

  function groupByMessageChunks(messages: Array<ChatMessage>, meId: number): Array<ChatMessageChunk> {

    let chunks = Array<ChatMessageChunk>();

    // group message by consecutive origin
    messages.forEach((msg: ChatMessage) => {

      let currentChunk: ChatMessageChunk | undefined = chunks[chunks.length - 1];

      // if new run or change of message origin, start a new chunk
      if (currentChunk === undefined || currentChunk.origin !== getChatMessageOrigin(msg, meId)) {
        chunks.push(createMessageChunk(getChatMessageOrigin(msg, meId), [msg]));;
      } else {
        // otherwise append to the last chunk
        currentChunk.messages.push(msg);
      }

    }, Array<Array<ChatMessage>>());

    return chunks;
  }

  function createMessageChunk(origin: ChatMessageOrigin, messages: Array<ChatMessage>): ChatMessageChunk {
    return {
      origin,
      messages,
      key: `messageChunk${messages[0].id}-${messages[messages.length - 1].id}`,
    }
  }

  const messageDateGroups: Ref<Array<ChatMessageDateGroup>> = computed(() => meStore.me !== null ? groupByMessageDateGroups(messages.value, meStore.me!.id) : []);

  return {
    messageDateGroups,
  }

};

export { useChat, useChatMessage, useChatMessageList };
