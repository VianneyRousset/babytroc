import type { ChatMessageType as ChatMessageTypeT } from '#build/types/open-fetch/schemas/api'

/**
 * Get the origin (me / interlocutor / system) of the chat mesage.
 **/
export function getChatMessageOrigin<
  MessageT extends {
    message_type: ChatMessageTypeT
    sender_id: number | null
  },
  UserT extends { id: number },
>(
  message: MessageT,
  me: UserT,
): ChatMessageOrigin {
  return (message.message_type === ChatMessageType.text
    ? (message.sender_id === me.id ? 'me' : 'interlocutor')
    : 'system'
  )
}
