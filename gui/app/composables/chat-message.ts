import type { ChatMessageType as ChatMessageTypeT } from '#build/types/open-fetch/schemas/api'
import { DateTime } from 'luxon'

/**
 * List all messages of the chat.
 **/
export function useChatMessages<
  ChatT extends { id: string },
>(
  chat: MaybeRefOrGetter<ChatT>,
): {
  messages: Ref<Array<ChatMessage>>
  isLoading: Ref<boolean>
  error: Ref<Error | null>
  end: Ref<boolean>
  loadMore: () => void
} {
  const liveMessages: Ref<Array<ChatMessage>> = useLiveChatStore().getChatMessages(() => toValue(chat).id)

  const { data: queriedMessages, isLoading, error, end, loadMore } = useApiPaginatedQuery(
    '/v1/me/chats/{chat_id}/messages', {
      key: () => ['me', 'chat', toValue(chat).id, 'messages'],
      path: () => ({ chat_id: toValue(chat).id }),
    })

  const messages = computed<Array<ChatMessage>>(() => [...(new Map([
    ...unref(queriedMessages),
    ...unref(liveMessages),
  ].map(msg => [msg.id, msg]))).values()])

  return { messages, isLoading, error, end, loadMore }
}

export function useSendChatMessage<
  ChatT extends { id: string },
>(
  chat: MaybeRefOrGetter<ChatT>,
) {
  const { $api } = useNuxtApp()

  const { mutateAsync: send, ...mutation } = useMutation({
    mutation: (text: string) =>
      $api('/v1/me/chats/{chat_id}/messages', {
        method: 'POST',
        path: {
          chat_id: toValue(chat).id,
        },
        body: {
          text: text,
        },
      }),
    onSettled: () => {
      // queryCache.invalidateQueries({
      //   key: ['me', 'borrowings', 'requests'],
      // })
      // queryCache.invalidateQueries({ key: ['chats'] })
      // queryCache.invalidateQueries({ key: ['chats', chatId, 'messages'] })
    },
  })

  return { send, ...mutation }
}

/**
 * Get the origin (me / interlocutor / system) of the chat mesage.
 **/
export function useChatMessageOrigin<
  MessageT extends { message_type: ChatMessageTypeT, sender_id: number | null },
  UserT extends { id: number },
>(
  message: MaybeRefOrGetter<MessageT>,
  me: MaybeRefOrGetter<UserT>,
): {
  origin: Ref<ChatMessageOrigin>
} {
  const origin = computed<ChatMessageOrigin>(() => getChatMessageOrigin(toValue(message), toValue(me)))
  return { origin }
}

/**
 * Format chat message time (creation date).
 **/
export function useChatMessageTime<
  MessageT extends { creation_date: string },
>(
  message: MaybeRefOrGetter<MessageT>,
) {
  return {
    formattedHour: DateTime.fromISO(
      toValue(message).creation_date,
    ).toLocaleString(DateTime.TIME_SIMPLE),
  }
}
