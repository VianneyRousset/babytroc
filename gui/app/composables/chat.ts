import { ChatMessageType } from "#build/types/open-fetch/schemas/api";
import { storeToRefs } from "pinia";
import { toValue, type MaybeRefOrGetter } from "vue";

import { DateTime } from "luxon";
import { groupBy } from "lodash";
import { useChatExtraMessagesStore } from "~/stores/chats";

export function useChatRoles(
	chat: MaybeRefOrGetter<Chat>,
	me: MaybeRefOrGetter<User>,
) {
	const isUserBorrowing = computed(
		() => toValue(chat).borrower.id === toValue(me).id,
	);
	const interlocutor = computed(() =>
		toValue(isUserBorrowing) ? toValue(chat).owner : toValue(chat).borrower,
	);

	return {
		isUserBorrowing,
		interlocutor,
	};
}

export function useChatMessageOrigin(
	message: MaybeRefOrGetter<ChatMessage>,
	me: MaybeRefOrGetter<User>,
): { origin: Ref<ChatMessageOrigin> } {
	const origin = computed<ChatMessageOrigin>(() =>
		toValue(message).message_type === ChatMessageType.text
			? toValue(message).sender_id === toValue(me).id
				? "me"
				: "interlocutor"
			: "system",
	);

	return { origin };
}

export function useChatMessageTime(message: MaybeRefOrGetter<ChatMessage>) {
	return {
		formattedHour: DateTime.fromISO(
			toValue(message).creation_date,
		).toLocaleString(DateTime.TIME_SIMPLE),
	};
}

export function useGroupChatMessages(
	messages: MaybeRefOrGetter<Array<ChatMessage>>,
	me: MaybeRefOrGetter<User>,
) {
	return {
		dateGroups: computed(() => {
			const _messages = toValue(messages);
			const _me = toValue(me);

			// group message by creation date
			const groups = groupBy(
				_messages,
				({ creation_date }: { creation_date: string }) =>
					DateTime.fromISO(creation_date).toISODate() ?? "",
			) as Record<string, Array<ChatMessage>>;

			// sort groups by min message id and convert into chunks
			return Object.entries(groups)
				.sort(
					([_a, a], [_b, b]) =>
						Math.min.apply(b.map((msg) => msg.id)) -
						Math.min.apply(a.map((msg) => msg.id)),
				)
				.map(([date, _messages]) =>
					createMessageDateGroup(date, _messages, _me),
				);
		}),
	};
}

export function useChats() {
	// add message to the proper extra chat messages store
	function addMessage(msg: ChatMessage) {
		const chatId = msg.chat_id;
		const extraMessagesStore = useChatExtraMessagesStore(chatId);
		console.log("add msg to store", extraMessagesStore);
		extraMessagesStore.addMessage(msg);
	}

	return {
		addMessage,
	};
}

export function useChatMessages(chatId: MaybeRefOrGetter<string>) {
	const { data: messagesPage, loadMore } = useChatMessagesListQuery(chatId);
	const extraMessagesStore = computed(() =>
		useChatExtraMessagesStore(toValue(chatId)),
	);
	const messages: Ref<Array<ChatMessage>> = computed(() => {
		const _messages: Map<number, ChatMessage> = new Map(
			unref(messagesPage).data?.map((msg) => [msg.id, msg]) ?? [],
		);
		const _extraMessagesStore = unref(extraMessagesStore);
		const _extraMessages: Map<number, ChatMessage> =
			_extraMessagesStore.messages;
		return Array.from(new Map([..._messages, ..._extraMessages]).values());
	});

	const addMessage = (msg: ChatMessage) =>
		unref(extraMessagesStore).addMessage(msg);

	return {
		messages,
		end: computed(() => unref(messagesPage).end),
		loadMore,
		addMessage,
	};
}

function createMessageDateGroup(
	date: string,
	messages: Array<ChatMessage>,
	user: User,
): ChatMessageDateGroup {
	return {
		date,
		formattedDate: formatRelativeDate(DateTime.fromISO(date)),
		chunks: groupByMessageChunks(
			messages.sort((a, b) => b.id - a.id),
			user,
		),
	};
}

function groupByMessageChunks(
	messages: Array<ChatMessage>,
	user: User,
): Array<ChatMessageChunk> {
	const chunks = Array<ChatMessageChunk>();

	// group message by consecutive origin
	for (const msg of messages) {
		const currentChunk: ChatMessageChunk | undefined =
			chunks[chunks.length - 1];

		// if new run or change of message origin, start a new chunk
		const origin = unref(useChatMessageOrigin(msg, user).origin);
		if (currentChunk === undefined || currentChunk.origin !== origin) {
			chunks.push(createMessageChunk(origin, [msg]));
		} else {
			// otherwise append to the last chunk
			currentChunk.messages.push(msg);
		}
	}

	return chunks;
}

function createMessageChunk(
	origin: ChatMessageOrigin,
	messages: Array<ChatMessage>,
): ChatMessageChunk {
	return {
		origin,
		messages,
		key: `messageChunk${messages[0]?.id}-${messages[messages.length - 1]?.id}`,
	};
}
