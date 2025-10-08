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
  loading: Ref<boolean>
  error: Ref<boolean>
  end: Ref<boolean>
  loadMore: () => void
} {
  const messages = ref(Array<ChatMessage>())
  const loading = ref(false)
  const error = ref(false)
  const end = ref(true)
  function loadMore() {}

  return { messages, loading, error, end, loadMore }
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
