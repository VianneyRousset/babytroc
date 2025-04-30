<script setup lang="ts">
import { Box } from "lucide-vue-next";

// get chat ID from route
const route = useRoute();
const chatId = String(route.params.chat_id);

// get main header bar height to offset content
const { height: mainHeaderHeight } = useElementSize(
	useTemplateRef("main-header"),
);

const {loggedIn} = useAuth();

watch(loggedIn, (state) => {
  if (state === false) navigateTo("/chats");
})

// current tab
const { currentTab } = useTab();

// query data
const { data: chat } = useChatQuery(chatId);
const { data: me } = useMeQuery();

// interlocutor
const interlocutor = computed(() => {
	const _chat = unref(chat);
	const _me = unref(me);

	if (_chat && _me) {
		const { interlocutor: _interlocutor } = useChatRoles(_chat, _me);
		return unref(_interlocutor);
	}

	return null;
});
</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar ref="main-header" :scrollOffset="32">
      <AppBack />
      <h1 v-if="interlocutor" :title="interlocutor.name">{{ interlocutor.name }}</h1>

      <!-- Dropdown menu -->
      <DropdownMenu v-if="chat">
        <NuxtLink :to="{ name: 'chats-item-item_id', params: { item_id: chat.item.id } }" class="reset-link">
          <DropdownMenuItem>
            <Box :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
            <div>Voir l'objet</div>
          </DropdownMenuItem>
        </NuxtLink>
      </DropdownMenu>

    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <ChatPresentation v-if="chat && me" ref="main" :chat="chat" :me="me" class="main app-content" />
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
