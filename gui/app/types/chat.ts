import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

export type Chat = ApiResponse<'list_client_chats_v1_me_chats_get'>[number]
export type ChatQuery = ApiRequestQuery<'list_client_chats_v1_me_chats_get'>
export type ChatMessage = ApiResponse<'list_client_chat_messages_v1_me_chats__chat_id__messages_get'>[number]
export type ChatMessageQuery = ApiRequestQuery<'list_client_chat_messages_v1_me_chats__chat_id__messages_get'>

export type ChatMessageSender = 'me' | 'interlocutor'
export type ChatMessageOrigin = 'me' | 'interlocutor' | 'system'

export type ChatMessageChunk = {
  origin: ChatMessageOrigin
  messages: Array<ChatMessage>
  key: string
}

export type ChatMessageDateGroup = {
  date: string
  formattedDate: string
  chunks: Array<ChatMessageChunk>
}
