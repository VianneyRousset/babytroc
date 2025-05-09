import { defineStore } from "pinia";

export const useExtraChatsStore = defineStore("extra-chats", () => {
	const { $api } = useNuxtApp();
	const chats = reactive(new Map<string, Chat>());

	async function ensureChat(chatId: string): Promise<Chat> {
		const chat = chats.get(chatId);

		// chat alredy exists, return it
		if (chat !== undefined) return chat;

		// chat doesn't exist, load it
		const newChat: Chat = await $api("/v1/me/chats/{chat_id}", {
			path: {
				chat_id: chatId,
			},
		});
		chats.set(newChat.id, newChat);
		return newChat;
	}

	async function setMessage(msg: ChatMessage) {
		// update chat last message id if chat is already loaded
		const chat = await ensureChat(msg.chat_id);
		chat.last_message_id = Math.max(chat.last_message_id, msg.id);

		// add message to chat extra messages
		const extraMessagesStore = useChatExtraMessagesStore(msg.chat_id);
		extraMessagesStore.setMessage(msg);
	}

	return {
		ensureChat,
		setMessage,
		chats,
	};
});

export const useChatExtraMessagesStore = (chatId: string) => {
	const storeId = `chat-${chatId}-extra-messages`;
	const definition = defineStore(storeId, () => {
		const messages = reactive(new Map<number, ChatMessage>());

		function setMessage(msg: ChatMessage) {
			if (msg.chat_id !== chatId)
				throw new Error(
					`Cannot add message with chatId ${msg.chat_id} in store ${storeId}.`,
				);

			messages.set(msg.id, msg);
		}

		return {
			setMessage,
			messages,
		};
	});
	return definition();
};
