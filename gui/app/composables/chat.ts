import { ChatMessageType } from "#build/types/open-fetch/schemas/api";
import { storeToRefs } from "pinia";
import { toValue, type MaybeRefOrGetter } from "vue";

import { DateTime } from "luxon";
import { groupBy } from "lodash";

export function useChats() {
	const { data: chatPages, loadMore } = useChatsListQuery();

	const extraChatsStore = useExtraChatsStore();
	const { chats: extraChats } = storeToRefs(extraChatsStore);
	const chats: Ref<Array<Chat>> = computed(() => {
		const _chats: Map<string, Chat> = new Map(
			unref(chatPages).data.map((chat) => [chat.id, chat]),
		);
		const _extraChats: Map<string, Chat> = unref(extraChats);
		return Array.from(new Map([..._chats, ..._extraChats]).values()).sort(
			(a, b) => b.last_message_id - a.last_message_id,
		);
	});

	return {
		chats,
		end: computed(() => unref(chatPages).end),
		loadMore,
		setMessage: extraChatsStore.setMessage,
	};
}

export function useChatMessages(chatId: MaybeRefOrGetter<string>) {
	const { data: messagePages, loadMore } = useChatMessagesListQuery(chatId);
	const extraMessagesStore = computed(() =>
		useChatExtraMessagesStore(toValue(chatId)),
	);
	const messages: Ref<Array<ChatMessage>> = computed(() => {
		const _messages: Map<number, ChatMessage> = new Map(
			unref(messagePages).data?.map((msg) => [msg.id, msg]) ?? [],
		);
		const _extraMessagesStore = unref(extraMessagesStore);
		const _extraMessages: Map<number, ChatMessage> =
			_extraMessagesStore.messages;
		return Array.from(new Map([..._messages, ..._extraMessages]).values());
	});

	const setMessage = (msg: ChatMessage) =>
		unref(extraMessagesStore).setMessage(msg);

	return {
		messages,
		end: computed(() => unref(messagePages).end),
		loadMore,
		addMessage: setMessage,
	};
}

export function useChatMessageIsNew(
	msg: MaybeRefOrGetter<ChatMessage>,
	me: MaybeRefOrGetter<User>,
) {
	const { sender } = useChatMessageSender(msg, me);
	const isNew: Ref<boolean> = computed(() =>
		unref(sender) === "me" ? false : !toValue(msg).seen,
	);

	return { isNew };
}

export function useChatHasNewMessages(
	chat: MaybeRefOrGetter<Chat>,
	me: MaybeRefOrGetter<User>,
): { hasNewMessages: Ref<boolean> } {
	const { messages } = useChatMessages(computed(() => toValue(chat).id));

	return {
		hasNewMessages: computed(() =>
			unref(messages).some(
				(msg) => unref(useChatMessageIsNew(msg, me).isNew) === true,
			),
		),
	};
}

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

export function useChatMessageSender(
	msg: MaybeRefOrGetter<ChatMessage>,
	me: MaybeRefOrGetter<User>,
): { sender: Ref<ChatMessageSender> } {
	return {
		sender: computed(() =>
			toValue(msg).sender_id === toValue(me).id ? "me" : "interlocutor",
		),
	};
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
			const _messages = toValue(messages).sort((a, b) => b.id - a.id);
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
