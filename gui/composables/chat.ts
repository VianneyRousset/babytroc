const useChat = (chat: Ref<Chat | null>) => {

  const meStore = useMeStore();

  const isUserBorrowing: Ref<boolean | null> = computed(() => {

    if (chat.value === null || meStore.me === null)
      return null;

    return chat.value.borrower.id === meStore.me.id;

  });

  const interlocutor: Ref<UserPreview | null> = computed(() => {

    if (chat.value === null || isUserBorrowing.value === null)
      return null

    return isUserBorrowing.value ? chat.value.owner : chat.value.borrower;
  });

  const item: Ref<ItemPreview | null> = computed(() => chat.value?.item ?? null);

  return {
    isUserBorrowing,
    interlocutor,
    item,
  }
};

export { useChat };
