export function useChat(chatId: MaybeRefOrGetter<string>) {
  const { data: chat, ...query } = useApiQuery(
    '/v1/me/chats/{chat_id}', {
      key: () => ['me', 'chat', toValue(chatId)],
      path: () => ({ chat_id: toValue(chatId) }),
    })

  const { addMessage } = useLiveChatStore()

  return { addMessage, chat, ...query }
}

export function useChatHot<
  ChatT extends { id: string },
>(
  chat: MaybeRefOrGetter<ChatT>,
) {
  const { me } = useMe()

  const liveChatStore = useLiveChatStore()
  const messages: Ref<Array<ChatMessage>> = liveChatStore.getChatMessages(() => toValue(chat).id)

  const hot = computed(() => {
    const _me = unref(me)
    const _messages: Array<ChatMessage> = unref(messages)
    return _me != null && _messages.some(msg => getChatMessageHot(msg, _me))
  })

  return { hot }
}

/**
 * List of chats of the client.
 **/
export function useChats(): {
  chats: Ref<Array<Chat>>
  isLoading: Ref<boolean>
  error: Ref<Error | null>
  end: Ref<boolean>
  loadMore: () => Promise<void>
  addMessage: (msg: ChatMessage) => void
  hot: Ref<boolean>
} {
  const { messages, chats: liveChats } = storeToRefs(useLiveChatStore())
  const { data: queriedChats, ...query } = useChatsQuery()

  const { addMessage } = useLiveChatStore()

  const { me } = useMe()

  // combine queried chats and live chats
  const chats = computed<Array<Chat>>(() => [...(new Map([
    ...unref(queriedChats),
    ...unref(liveChats),
  ].map(chat => [chat.id, chat]))).values()].sort((a, b) => b.last_message_id - a.last_message_id))

  const hot = computed(() => {
    const _me = unref(me)
    return _me != null && unref(messages).some(msg => getChatMessageHot(msg, _me))
  })

  return { chats, ...query, addMessage, hot }
}

/**
 * Get if the client is the borrower and access to the interlocutor user.
 **/
export function useChatRoles<
  UserT extends { id: number },
  ChatT extends { borrower: UserT, owner: UserT },
  MeT extends { id: number },
>(
  chat: MaybeRefOrGetter<ChatT>,
  me: MaybeRefOrGetter<MeT>,
): {
  isUserBorrowing: Ref<boolean>
  interlocutor: Ref<ChatT['borrower'] | ChatT['owner']>
} {
  const isUserBorrowing = computed(
    () => toValue(chat).borrower.id === toValue(me).id,
  )
  const interlocutor = computed(() =>
    toValue(isUserBorrowing) ? toValue(chat).owner : toValue(chat).borrower,
  )

  return {
    isUserBorrowing,
    interlocutor,
  }
}
