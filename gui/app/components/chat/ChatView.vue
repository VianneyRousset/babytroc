<script setup lang="ts">
import { ChatMessages } from '#components'

const props = defineProps<{
  chatId: string
}>()

const { chatId } = toRefs(props)

const { chat, isLoading: chatIsLoading, addMessage } = useChat(chatId)

// TODO add meIsLoading
const { me } = useMe()
const { messages, isLoading: messagesIsLoading, loadMore, end } = useChatMessages(() => ({ id: unref(chatId) }))

watch(messages, v => console.log('messages', v.length))

const scroller = useTemplateRef<HTMLElement>('scroller')

const outbox = ref('')

const { send, isLoading: sendIsLoading } = useSendChatMessage(() => ({ id: unref(chatId) }))

useInfiniteScroll(
  scroller,
  () => {
    console.log('loadMore')
    loadMore()
  },
  {
    canLoadMore: () => !unref(end),
    direction: 'top',
    distance: 300,
    interval: 1000,
    offset: {
      // distance does not work if flex-direction: column-reverse is used
      bottom: 300,
    },
  },
)

const { y } = useScroll(scroller)
const { height } = useElementSize(useTemplateRef<HTMLElement>('messages'))

watch(height, (newH, oldH) => {
  y.value = unref(y) + newH - oldH
})

const { $toast } = useNuxtApp()

async function sendMessage() {
  let msg: ChatMessage | undefined = undefined

  try {
    msg = await send(unref(outbox))
  }
  catch (error) {
    $toast.error('Envoi échoué')
    throw error
  }

  if (msg)
    addMessage(msg)

  outbox.value = ''
}
</script>

<template>
  <div class="ChatView">
    <WithLoading :loading="chatIsLoading || ((messages == null || messages.length == 0) && messagesIsLoading)">
      <WithFloating>
        <div
          ref="scroller"
          class="scroller"
        >
          <ChatMessages
            v-if="me && chat && messages"
            ref="messages"
            class="with-floating-padding"
            :chat="chat"
            :me="me"
            :messages="messages"
          />
          <LoadingAnimation v-if="messagesIsLoading" />
        </div>

        <template #floating>
          <ChatMessageInput
            v-model="outbox"
            :loading="sendIsLoading"
            @submit="sendMessage"
          />
        </template>
      </WithFloating>
    </WithLoading>
  </div>
</template>

<style lang="scss" scoped>
.ChatView {

  .WithFloating {
    width: 100%;
    height: 100%;
  }

  .scroller {
    display: flex;
    flex-direction: column-reverse;
    align-items: stretch;
    width: 100%;
    height: 100%;
    overflow-x: hidden;
    overflow-y: scroll;

    .ChatMessages {
      padding-top: 2em;
      padding-left: clamp(0em, 1vw, 2em);
      padding-right: clamp(0em, 1vw, 2em);
    }

    .LoadingAnimation {
      padding: 2em 0;
    }
  }

  .ChatMessageInput {
    padding: 1em;
  }

  & > .LoadingAnimation {
    flex: 2;
    padding-top: 40%;
  }
}
</style>
