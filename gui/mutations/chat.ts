export const useSendMessageMutation = defineMutation(() => {

  const { $api } = useNuxtApp();
  const queryCache = useQueryCache();

  return useMutation({
    mutation: ({ chatId, text }: { chatId: string, text: string }) => $api("/v1/me/chats/{chat_id}/messages", {
      method: "POST",
      path: {
        chat_id: chatId,
      },
      body: {
        text: text,
      },
    }),
    onSettled: (_data, _error, { chatId }) => {
      queryCache.invalidateQueries({
        key: ["me", "borrowings", "requests"]
      });
      queryCache.invalidateQueries({ key: ["chats"] });
      queryCache.invalidateQueries({ key: ["chat", chatId, "messages"] });
    },
  });
});
