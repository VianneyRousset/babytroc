import { groupBy } from 'lodash'
import { DateTime } from 'luxon'
import type { ChatMessageType as ChatMessageTypeT } from '#build/types/open-fetch/schemas/api'
/**
 * Chat message grouping.
 *
 *  ┌DateGroup────────────────────────┐
 *  │                                 │
 *  │ ┌Chunk (origin: me)───────────┐ │
 *  │ │                             │ │
 *  │ │  message1                   │ │
 *  │ │  message2                   │ │
 *  │ │  message3                   │ │
 *  │ │                             │ │
 *  │ └─────────────────────────────┘ │
 *  │ ┌Chunk (origin: interlocutor)─┐ │
 *  │ │                             │ │
 *  │ │  message4                   │ │
 *  │ │  message5                   │ │
 *  │ │                             │ │
 *  │ └─────────────────────────────┘ │
 *  │                                 │
 *  └─────────────────────────────────┘
 *
 *  ┌DateGroup────────────────────────┐
 *  │                                 │
 *  │ ┌Chunk (origin: system)───────┐ │
 *  │ │                             │ │
 *  │ │  message6                   │ │
 *  │ │  message7                   │ │
 *  │ │  message8                   │ │
 *  │ │                             │ │
 *  │ └─────────────────────────────┘ │
 *  └─────────────────────────────────┘
 **/

export type ChatMessageDateGroup<MessageT> = {
  date: string
  formattedDate: string
  chunks: Array<ChatMessageChunk<MessageT>>
  minMessageId: number
}

export type ChatMessageChunk<MessageT> = {
  origin: ChatMessageOrigin
  messages: Array<MessageT>
  key: string
}

/**
 * Group message in date groups.
 **/
export function useChatMessageDateGroups<
  MessageT extends {
    id: number
    creation_date: string
    message_type: ChatMessageTypeT
    sender_id: number | null
  },
  UserT extends { id: number },
>(
  messages: MaybeRefOrGetter<Array<MessageT>>,
  me: MaybeRefOrGetter<UserT>,
): {
  dateGroups: Ref<Array<ChatMessageDateGroup<MessageT>>>
} {
  const dateGroups = computed<Array<ChatMessageDateGroup<MessageT>>>(() => {
    const _messages = toValue(messages)
    const _me = toValue(me)

    // group messages by date and create dateGroups
    const _dateGroups = Object.entries(groupBy(
      _messages,
      ({ creation_date }) => DateTime.fromISO(creation_date).toISODate() ?? '',
    )).map(([date, _messages]) => createMessageDateGroup(date, _messages, _me))

    // sort groups by min message id and convert into chunks
    return _dateGroups.sort((a, b) => b.minMessageId - a.minMessageId)
  })

  return { dateGroups }
}

/**
 * Create a date group for `date` containing `messages`.
 **/
function createMessageDateGroup<
  MessageT extends {
    id: number
    creation_date: string
    message_type: ChatMessageTypeT
    sender_id: number | null
  },
  UserT extends { id: number },
>(
  date: string,
  messages: Array<MessageT>,
  me: UserT,
): ChatMessageDateGroup<MessageT> {
  return {
    date,
    formattedDate: formatRelativeDate(DateTime.fromISO(date)),
    chunks: groupByMessageChunks(
      messages.sort((a, b) => b.id - a.id),
      me,
    ),
    minMessageId: Math.min.apply(messages.map(msg => msg.id)),
  }
}

function createMessageChunk<
  MessageT extends {
    id: number
  },
>(
  origin: ChatMessageOrigin,
  messages: Array<MessageT>,
): ChatMessageChunk<MessageT> {
  return {
    origin,
    messages,
    key: `messageChunk${messages[0]?.id}-${messages[messages.length - 1]?.id}`,
  }
}

// group message by chunks of same consecutive origin
function groupByMessageChunks<
  MessageT extends {
    id: number
    message_type: ChatMessageTypeT
    sender_id: number | null
  },
  UserT extends { id: number },
>(
  messages: Array<MessageT>,
  me: UserT,
): Array<ChatMessageChunk<MessageT>> {
  return messages.reduce((acc, msg) => {
    const origin = getChatMessageOrigin(msg, me)

    if (acc.length && (acc[acc.length - 1] as ChatMessageChunk<MessageT>).origin === getChatMessageOrigin(msg, me))
      (acc[acc.length - 1] as ChatMessageChunk<MessageT>).messages.push(msg)
    else
      acc.push(createMessageChunk<MessageT>(origin, [msg]))

    return acc
  }, Array<ChatMessageChunk<MessageT>>())
}
