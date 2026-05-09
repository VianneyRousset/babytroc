import type { ApiRequestQuery, ApiResponse } from "#open-fetch";

export type Chat = ApiResponse<"list_client_chats_v1_me_chats_get">[number];
export type ChatMessage =
	ApiResponse<"list_client_chat_messages_v1_me_chats__chat_id__messages_get">[number];
export type ChatMessageQuery =
	ApiRequestQuery<"list_client_chat_messages_v1_me_chats__chat_id__messages_get">;

// Re-define the enum locally since #build paths can't be resolved at runtime
// by Vite's environment API. Values must match the API's ChatMessageType enum.
export enum ChatMessageType {
	text = 1,
	loan_request_created = 2,
	loan_request_cancelled = 3,
	loan_request_accepted = 4,
	loan_request_rejected = 5,
	loan_started = 6,
	loan_ended = 7,
	item_not_available = 8,
	item_available = 9,
}
export type ChatMessageSender = "me" | "interlocutor";
export type ChatMessageOrigin = "me" | "interlocutor" | "system";
