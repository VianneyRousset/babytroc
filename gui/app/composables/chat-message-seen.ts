/**
 * Get chat message seen status and update it.
 *
 * If `monitor` is given, the visibility of the component `monitor` is checked. When the latter is
 * visible for more than `timeout` ms, the function `markAsSeen()` is automatically called.
 *
 * @return `hot`, true if the message is addressed to me and not seen.
 *
 * @return `markAsSeen()`, mark message as seen. The latter function safe to call even if the message
 *                         is already seen and whatever is the origin.
 **/
export function useChatMessageSeen<
  MessageT extends { id: number, chat_id: string, seen: boolean, sender_id: number | null },
  UserT extends { id: number },
>(
  message: MaybeRefOrGetter<MessageT>,
  me: MaybeRefOrGetter<UserT>,
  options: {
    monitor?: MaybeRefOrGetter<HTMLElement | undefined | null>
    timeout?: MaybeRefOrGetter<number>
  },
): {
  hot: MaybeRefOrGetter<boolean>
  markAsSeen: () => Promise<void>
} {
  // if the element `monitor` is visible for `timeout` ms, call `markAsSeen`
  const { value: visible } = useThrottle(useElementVisibility(() => toValue(options.monitor)), () => toValue(options.timeout) ?? 2000)
  const stop = watch(visible, state => state === true && markAsSeen(), { immediate: true })

  // is unseen for me
  const hot = computed(() => getChatMessageHot(toValue(message), toValue(me)))

  // mutation to mark as seen
  const { asyncStatus, mutateAsync } = useMarkChatMessageAsSeenMutation(message)

  async function markAsSeen() {
    const _msg = toValue(message)

    // skip if message is already marked as seen, if the sender is me or if a request
    // is already pending
    if (_msg.seen || _msg.sender_id === toValue(me).id || toValue(asyncStatus) === 'loading') return

    await mutateAsync()
  }

  tryOnUnmounted(stop)

  return {
    hot,
    markAsSeen,
  }
}
