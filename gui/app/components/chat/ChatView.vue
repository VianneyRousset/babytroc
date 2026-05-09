<script setup lang="ts">
const props = defineProps<{
	chatId: string;
}>();

const { chatId } = toRefs(props);

const { chat, isLoading: chatIsLoading, addMessage } = useChat(chatId);

// report
const _reportDialogOpen = ref(false);
const { mutateAsync: reportChat } = useReportChatMutation(chatId);

// TODO add meIsLoading
const { me } = useMe();
const {
	messages,
	isLoading: messagesIsLoading,
	loadMore,
	end,
} = useChatMessages(() => ({ id: unref(chatId) }));

const scroller = useTemplateRef<HTMLElement>("scroller");

const outbox = ref("");

const { send, isLoading: sendIsLoading } = useSendChatMessage(() => ({
	id: unref(chatId),
}));

useInfiniteScroll(scroller, loadMore, {
	canLoadMore: () => !unref(end),
	direction: "top",
	distance: 500,
	offset: {
		// distance does not work if flex-direction: column-reverse is used
		bottom: 500,
	},
});

const { y } = useScroll(scroller);
const { height } = useElementSize(useTemplateRef<HTMLElement>("messages-list"));

watch(height, (newH, oldH) => {
	y.value = unref(y) + newH - oldH;
});

const { $toast } = useNuxtApp();

async function _sendMessage() {
	let msg: ChatMessage | undefined;

	try {
		msg = await send(unref(outbox));
	} catch (error) {
		$toast.error("Envoi échoué");
		throw error;
	}

	if (msg) addMessage(msg);

	outbox.value = "";
}
</script>

<template>
  <div class="ChatView">
    <div
      v-if="chat"
      class="chat-menu"
    >
      <DropdownMenu>
        <DropdownItem
          :icon="Package"
          :target="`/explore/item/${chat.item.id}`"
        >
          Voir l'objet
        </DropdownItem>
        <DropdownItem
          :icon="ShieldAlert"
          red
          @click="reportDialogOpen = true"
        >
          Signaler
        </DropdownItem>
      </DropdownMenu>
    </div>

    <!-- Report dialog -->
    <ReportDialog
      v-model="reportDialogOpen"
      :submit="reportChat"
      :context="`chat:${chatId}`"
    />

    <WithLoading :loading="chatIsLoading || ((messages == null || messages.length == 0) && messagesIsLoading)">
      <WithFloating>
        <div
          ref="scroller"
          class="scroller"
        >
          <ChatMessages
            v-if="me && chat && messages"
            ref="messages-list"
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
  position: relative;

  .chat-menu {
    position: absolute;
    top: $space-3;
    right: $space-3;
    z-index: 2;
  }

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
    scrollbar-width: none;

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
