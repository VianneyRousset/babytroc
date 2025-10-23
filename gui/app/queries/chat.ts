export const useChatsQuery = defineQuery(() => useApiPaginatedQuery('/v1/me/chats', {
  key: ['me', 'chats'],
}))
