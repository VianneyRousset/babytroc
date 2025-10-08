/* NEW */

export function useMarkChatMessageAsSeenMutation<
  MessageT extends { id: number, chat_id: string },
>(
  message: MaybeRefOrGetter<MessageT>,
) {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: async () => {
      const _msg = toValue(message)
      return await $api('/v1/me/chats/{chat_id}/messages/{message_id}/see', {
        method: 'post',
        path: {
          chat_id: _msg.chat_id,
          message_id: _msg.id,
        },
      })
    },
  })
}

/* OLD */

export const useSendMessageMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: ({ chatId, text }: { chatId: string, text: string }) =>
      $api('/v1/me/chats/{chat_id}/messages', {
        method: 'POST',
        path: {
          chat_id: chatId,
        },
        body: {
          text: text,
        },
      }),
    onSettled: (_data, _error, { chatId }) => {
      queryCache.invalidateQueries({
        key: ['me', 'borrowings', 'requests'],
      })
      queryCache.invalidateQueries({ key: ['chats'] })
      queryCache.invalidateQueries({ key: ['chats', chatId, 'messages'] })
    },
  })
})
