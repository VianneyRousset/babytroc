import type { ApiResponse, ApiRequestQuery } from "#open-fetch";

declare global {
	type Chat = ApiResponse<"list_client_chats_v1_me_chats_get">[number];
	type ChatQuery = ApiRequestQuery<"list_client_chats_v1_me_chats_get">;
	type ChatMessage =
		ApiResponse<"list_client_chat_messages_v1_me_chats__chat_id__messages_get">[number];
	type ChatMessageQuery =
		ApiRequestQuery<"list_client_chat_messages_v1_me_chats__chat_id__messages_get">;

	type ChatMessageSender = "me" | "interlocutor";
	type ChatMessageOrigin = "me" | "interlocutor" | "system";

	type ChatMessageChunk = {
		origin: ChatMessageOrigin;
		messages: Array<ChatMessage>;
		key: string;
	};

	type ChatMessageDateGroup = {
		date: string;
		formattedDate: string;
		chunks: Array<ChatMessageChunk>;
	};
}

export type {
	Chat,
	ChatQuery,
	ChatMessage,
	ChatMessageQuery,
	ChatMessageOrigin,
	ChatMessageChunk,
	ChatMessageDateGroup,
};
