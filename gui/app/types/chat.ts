import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

export type Chat = ApiResponse<'list_client_chats_v1_me_chats_get'>[number]
export type ChatMessage = ApiResponse<'list_client_chat_messages_v1_me_chats__chat_id__messages_get'>[number]
export type ChatMessageQuery = ApiRequestQuery<'list_client_chat_messages_v1_me_chats__chat_id__messages_get'>

export { ChatMessageType } from '#build/types/open-fetch/schemas/api'
export type ChatMessageSender = 'me' | 'interlocutor'
export type ChatMessageOrigin = 'me' | 'interlocutor' | 'system'
