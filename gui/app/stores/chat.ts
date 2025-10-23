import { defineStore } from 'pinia'

export const useLiveChatStore = defineStore('live-chat', () => {
  // all the stored messages
  const messages = ref(new Map<number, ChatMessage>())

  // all the stored chats
  const chatIds = computed<Set<string>>(() => new Set([...unref(messages).values()].map(msg => msg.chat_id)))

  // add the given message to the collection of messages
  function addMessage(message: ChatMessage) {
    unref(messages).set(message.id, message)
  }

  // get all stored messages from the given chat ID
  function getChatMessages(chatId: MaybeRefOrGetter<string>): Ref<Array<ChatMessage>> {
    return computed(() => _getChatMessages(toValue(chatId)))
  }
  function _getChatMessages(chatId: string): Array<ChatMessage> {
    return [...unref(messages).values()].filter(msg => msg.chat_id == chatId)
  }

  // get last message in chat
  function _getChatLastMessage(chatId: string): ChatMessage | undefined {
    return _getChatMessages(chatId).sort((a, b) => b.id - a.id)[0]
  }

  const savedChats = ref(new Map<string, Chat>())

  async function ensureChat(chatId: string) {
    if (unref(savedChats).get(chatId)) return

    unref(savedChats).set(chatId, await $api('/v1/me/chats/{chat_id}', {
      path: {
        chat_id: chatId,
      },
    }))
  }

  const chats = computed<Array<Chat>>(() => {
    unref(chatIds).forEach(chatId => ensureChat(chatId))
    return [...unref(savedChats).values()].map(chat => ({
      ...chat,
      last_message_id: _getChatLastMessage(chat.id)?.id ?? 0,
    }))
  })

  const { $api } = useNuxtApp()

  async function prefetchMessages() {
    const chats = await $api('/v1/me/chats')

    await Promise.all(chats.map(chat => $api('/v1/me/chats/{chat_id}/messages', {
      path: { chat_id: chat.id },
    }).then(messages => messages.map(addMessage))))
  }

  prefetchMessages()

  return {
    messages: computed(() => [...unref(messages).values()]),
    chats,
    chatIds,
    addMessage,
    getChatMessages,
  }
})
