export function useChat(chatId: MaybeRefOrGetter<string | undefined>) {
  const { data: chat, ...query } = useApiQuery('/v1/me/chats/{chat_id}', {
    key: () => ['me', 'chat', toValue(chatId) ?? ''],
    path: () => ({
      chat_id: toValue(chatId) ?? '',
    }),
    enabled: () => toValue(chatId) != null,
  })

  const { addMessage } = useLiveChatStore()

  return { addMessage, chat, ...query }
}

/**
 * List of chats of the client.
 * TODO implement
 **/
export function useChats(): {
  chats: Ref<Array<Chat>>
  isLoading: Ref<boolean>
  error: Ref<Error | null>
  end: Ref<boolean>
  loadMore: () => Promise<void>
  hot: Ref<boolean>
  addMessage: (msg: ChatMessage) => void
} {
  const { data: chats, isLoading, error, end, loadMore } = useApiPaginatedQuery('/v1/me/chats', {
    key: ['me', 'chats'],
  })

  const hot = ref(true)
  const { addMessage } = useLiveChatStore()

  return { chats, isLoading, error, end, loadMore, hot, addMessage }
}

/**
 * Get if the client is the borrower and access to the interlocutor user.
 **/
// type ChatT<UserT extends { id: number }> = { borrower: UserT, owner: UserT }
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

/**
 * Get status of unseen message in chat.
 * TODO implement
 **/
export function useChatSeen<
  ChatT extends { id: string },
  UserT extends { id: number },
>(
  chat: MaybeRefOrGetter<ChatT>,
  me: MaybeRefOrGetter<UserT>,
): {
  hot: Ref<boolean>
} {
  const hot = computed(() => toValue(chat).id !== '')
  return { hot }
}
