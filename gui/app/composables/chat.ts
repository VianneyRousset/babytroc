import { storeToRefs } from 'pinia'
import { toValue, type MaybeRefOrGetter } from 'vue'

import { DateTime } from 'luxon'
import { groupBy } from 'lodash'
import { ChatMessageType } from '#build/types/open-fetch/schemas/api'

interface UserWithId {
  id: number
}

export function useChats() {
  const { data: chatPages, loadMore } = useChatsListQuery()
  const { data: me } = useMeQuery()

  const extraChatsStore = useExtraChatsStore()
  const { chats: extraChats } = storeToRefs(extraChatsStore)
  const chats: Ref<Array<Chat>> = computed(() => {
    const _chats: Map<string, Chat> = new Map(
      unref(chatPages).data.map(chat => [chat.id, chat]),
    )
    const _extraChats: Map<string, Chat> = unref(extraChats)
    return Array.from(new Map([..._chats, ..._extraChats]).values()).sort(
      (a, b) => b.last_message_id - a.last_message_id,
    )
  })
  const hasNewMessages: Ref<boolean> = computed(() => {
    const _chats = unref(chats)
    const _me = unref(me)
    if (_me === undefined)
      return false
    return _chats.some(chat => unref(useChatHasNewMessages(chat, _me).hasNewMessages) === true)
  })

  return {
    chats,
    end: computed(() => unref(chatPages).end),
    loadMore,
    setMessage: extraChatsStore.setMessage,
    hasNewMessages,
  }
}

export function useChatMessages(chatId: MaybeRefOrGetter<string>) {
  const { data: messagePages, loadMore } = useChatMessagesListQuery(chatId)
  const extraMessagesStore = computed(() =>
    useChatExtraMessagesStore(toValue(chatId)),
  )
  const messages: Ref<Array<ChatMessage>> = computed(() => {
    const _messages: Map<number, ChatMessage> = new Map(
      unref(messagePages).data?.map(msg => [msg.id, msg]) ?? [],
    )
    const _extraMessagesStore = unref(extraMessagesStore)
    const _extraMessages: Map<number, ChatMessage> = _extraMessagesStore.messages
    return Array.from(new Map([..._messages, ..._extraMessages]).values())
  })

  const setMessage = (msg: ChatMessage) =>
    unref(extraMessagesStore).setMessage(msg)

  return {
    messages,
    end: computed(() => unref(messagePages).end),
    loadMore,
    addMessage: setMessage,
  }
}

export function useChatMessageIsNew<T extends UserWithId>(
  msg: MaybeRefOrGetter<ChatMessage>,
  me: MaybeRefOrGetter<T>,
) {
  const { sender } = useChatMessageSender(msg, me)
  const isNew: Ref<boolean> = computed(() =>
    unref(sender) === 'me' ? false : !toValue(msg).seen,
  )

  return { isNew }
}

export function useChatHasNewMessages<T extends UserWithId>(
  chat: MaybeRefOrGetter<Chat>,
  me: MaybeRefOrGetter<T>,
): { hasNewMessages: Ref<boolean> } {
  const { messages } = useChatMessages(computed(() => toValue(chat).id))

  return {
    hasNewMessages: computed(() =>
      unref(messages).some(
        msg => unref(useChatMessageIsNew(msg, me).isNew) === true,
      ),
    ),
  }
}

export function useChatRoles<T extends UserWithId>(
  chat: MaybeRefOrGetter<Chat>,
  me: MaybeRefOrGetter<T>,
) {
  const isUserBorrowing = computed(
    () => toValue(chat).borrower.id === toValue(me).id,
  )
  const interlocutor = computed(() =>
    toValue(isUserBorrowing) ? toValue(chat).owner : toValue(chat).borrower,
  )

  return {
    isUserBorrowing,
    interlocutor,
  }
}

export function useChatMessageOrigin<T extends UserWithId>(
  message: MaybeRefOrGetter<ChatMessage>,
  me: MaybeRefOrGetter<T>,
): { origin: Ref<ChatMessageOrigin> } {
  const origin = computed<ChatMessageOrigin>(() =>
    toValue(message).message_type === ChatMessageType.text
      ? toValue(message).sender_id === toValue(me).id
        ? 'me'
        : 'interlocutor'
      : 'system',
  )

  return { origin }
}

export function useChatMessageSender<T extends UserWithId>(
  msg: MaybeRefOrGetter<ChatMessage>,
  me: MaybeRefOrGetter<T>,
): { sender: Ref<ChatMessageSender> } {
  return {
    sender: computed(() =>
      toValue(msg).sender_id === toValue(me).id ? 'me' : 'interlocutor',
    ),
  }
}

export function useChatMessageTime(message: MaybeRefOrGetter<ChatMessage>) {
  return {
    formattedHour: DateTime.fromISO(
      toValue(message).creation_date,
      ).toLocaleString(DateTime.TIME_SIMPLE),
  }
}
export function useGroupChatMessages<T extends UserWithId>(
  messages: MaybeRefOrGetter<Array<ChatMessage>>,
  me: MaybeRefOrGetter<T>,
) {
  return {
    dateGroups: computed(() => {
      const _messages = toValue(messages).sort((a, b) => b.id - a.id)
      const _me = toValue(me)

      // group message by creation date
      const groups = groupBy(
        _messages,
        ({ creation_date }: { creation_date: string }) =>
          DateTime.fromISO(creation_date).toISODate() ?? '',
      ) as Record<string, Array<ChatMessage>>

      // sort groups by min message id and convert into chunks
      return Object.entries(groups)
        .sort(
          ([_a, a], [_b, b]) =>
            Math.min.apply(b.map(msg => msg.id))
            - Math.min.apply(a.map(msg => msg.id)),
        )
        .map(([date, _messages]) =>
          createMessageDateGroup(date, _messages, _me),
        )
    }),
  }
}

function createMessageDateGroup<T extends UserWithId>(
  date: string,
  messages: Array<ChatMessage>,
  user: T,
): ChatMessageDateGroup {
  return {
    date,
    formattedDate: formatRelativeDate(DateTime.fromISO(date)),
    chunks: groupByMessageChunks(
      messages.sort((a, b) => b.id - a.id),
      user,
    ),
  }
}

function groupByMessageChunks<T extends UserWithId>(
  messages: Array<ChatMessage>,
  user: T,
): Array<ChatMessageChunk> {
  const chunks = Array<ChatMessageChunk>()

  // group message by consecutive origin
  for (const msg of messages) {
    const currentChunk: ChatMessageChunk | undefined = chunks[chunks.length - 1]

    // if new run or change of message origin, start a new chunk
    const origin = unref(useChatMessageOrigin(msg, user).origin)
    if (currentChunk === undefined || currentChunk.origin !== origin) {
      chunks.push(createMessageChunk(origin, [msg]))
    }
    else {
      // otherwise append to the last chunk
      currentChunk.messages.push(msg)
    }
  }

  return chunks
}

function createMessageChunk(
  origin: ChatMessageOrigin,
  messages: Array<ChatMessage>,
): ChatMessageChunk {
  return {
    origin,
    messages,
    key: `messageChunk${messages[0]?.id}-${messages[messages.length - 1]?.id}`,
  }
}
