import { defineStore } from "pinia";

export const useChatExtraMessagesStore = (chatId: string) => {
	const storeId = `chat-${chatId}-extra-messages`;
	const definition = defineStore(storeId, () => {
		const messages = reactive(new Map<number, ChatMessage>());

		function addMessage(msg: ChatMessage) {
			if (msg.chat_id !== chatId)
				throw new Error(
					`Cannot add message with chatId ${msg.chat_id} in store ${storeId}.`,
				);

			messages.set(msg.id, msg);
		}

		return {
			addMessage,
			messages,
		};
	});
	return definition();
};
