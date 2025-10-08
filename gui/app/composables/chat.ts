/**
 * List of chats of the client.
 * TODO implement
 **/
export function useChats(): {
  chats: Ref<Array<Chat>>
  loading: Ref<boolean>
  error: Ref<boolean>
  end: Ref<boolean>
  loadMore: () => void
  hasUnseenMessageForMe: Ref<boolean>
  addMessage: (msg: ChatMessage) => void
} {
  const chats = ref(Array<Chat>())
  const hasUnseenMessageForMe = ref(true)
  function addMessage(msg: ChatMessage) {
    console.log('addMessage', msg)
  }

  const loading = ref(false)
  const error = ref(false)
  const end = ref(true)
  function loadMore() {}

  return { chats, loading, error, end, loadMore, hasUnseenMessageForMe, addMessage }
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
  hasUnseenMessageForMe: Ref<boolean>
} {
  const hasUnseenMessageForMe = computed(() => toValue(chat).id !== '')
  return { hasUnseenMessageForMe }
}
