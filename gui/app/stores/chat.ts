import { defineStore } from 'pinia'

export const useLiveChatStore = defineStore('live-chat', () => {
  // all the stored messages
  const messages = ref(new Map<number, ChatMessage>())

  // all the stored chats
  const chatIds = computed<Set<string>>(() => new Set([...unref(messages).values()].map(msg => msg.chat_id)))

  const { $api } = useNuxtApp()

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
    return [...unref(savedChats).values()]
  })

  // add the given message to the collection of messages
  function addMessage(message: ChatMessage) {
    unref(messages).set(message.id, message)
  }

  // get all stored messages from the given chat ID
  function getChatMessages(chatId: MaybeRefOrGetter<string>): Ref<Array<ChatMessage>> {
    return computed(() => [...unref(messages).values()].filter(msg => msg.chat_id == toValue(chatId)))
  }

  return {
    messages,
    chats,
    chatIds,
    addMessage,
    getChatMessages,
  }
})

/*
export const useExtraChatsStore = defineStore('extra-chats', () => {
  const { $api } = useNuxtApp()

  async function ensureChat(chatId: string): Promise<Chat> {
    const chat = chats.get(chatId)

    // chat alredy exists, return it
    if (chat !== undefined) return chat

    // chat doesn't exist, load it
    const newChat: Chat = await $api('/v1/me/chats/{chat_id}', {
      path: {
        chat_id: chatId,
      },
    })
    chats.set(newChat.id, newChat)
    return newChat
  }

  async function setMessage(msg: ChatMessage) {
    // update chat last message id if chat is already loaded
    const chat = await ensureChat(msg.chat_id)
    chat.last_message_id = Math.max(chat.last_message_id, msg.id)

    // add message to chat extra messages
    const extraMessagesStore = useChatExtraMessagesStore(msg.chat_id)
    extraMessagesStore.setMessage(msg)
  }

  return {
    ensureChat,
    setMessage,
    chats,
  }
})

export const useChatExtraMessagesStore = (chatId: string) => {
  const storeId = `chat-${chatId}-extra-messages`
  const definition = defineStore(storeId, () => {
    const messages = reactive(new Map<number, ChatMessage>())

    function setMessage(msg: ChatMessage) {
      if (msg.chat_id !== chatId)
        throw new Error(
          `Cannot add message with chatId ${msg.chat_id} in store ${storeId}.`,
        )

      messages.set(msg.id, msg)
    }

    return {
      setMessage,
      messages,
    }
  })
  return definition()
}
*/
