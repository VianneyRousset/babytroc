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
