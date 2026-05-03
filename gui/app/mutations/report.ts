export function useReportItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: async (data: { message: string, context: string }) =>
      await $api('/v1/items/{item_id}/report', {
        method: 'POST',
        path: { item_id: toValue(itemId) },
        body: data,
      }),
  })
}

export function useReportChatMutation(chatId: MaybeRefOrGetter<string>) {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: async (data: { message: string, context: string }) =>
      await $api('/v1/me/chats/{chat_id}/report', {
        method: 'POST',
        path: { chat_id: toValue(chatId) },
        body: data,
      }),
  })
}

export function useReportUserMutation(userId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: async (data: { message: string, context: string }) =>
      await $api('/v1/users/{user_id}/report', {
        method: 'POST',
        path: { user_id: toValue(userId) },
        body: data,
      }),
  })
}
