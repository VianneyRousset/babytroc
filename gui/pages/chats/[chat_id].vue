<script setup lang="ts">

import { Box } from 'lucide-vue-next';

// get chat ID from route
const route = useRoute();
const chatId = String(route.params.chat_id);

// get main header bar height to offset content
const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

// current tab
const { currentTab } = useTab();

// get chat data
const { data: chat, refresh: refreshItem } = await useApi('/v1/me/chats/{chat_id}', {
  path: {
    chat_id: chatId,
  },
  key: `chats/${chatId}`
});
const { interlocutor, item } = useChat(chat);

// interlocutor
const { name: interlocutorName, avatarSeed: interlocutorAvatar } = useUserPreview(interlocutor);

// chat messages
const useChatMessagesStore = createChatMessagesStore(chatId);
const chatMessagesStore = useChatMessagesStore();

// chat input
const chatMessageInput = ref("");

// send message
async function submitMessage(msg: string) {
  await chatMessagesStore.send(msg);
  chatMessageInput.value = "";
}

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <AppBack />
      <h1 :title="interlocutorName ?? undefined">{{ interlocutorName ?? "..." }}</h1>

      <!-- Dropdown menu -->
      <DropdownMenu>

        <DropdownMenuItem class="DropdownMenuItem" asChild>
          <NuxtLink v-if="item" :to="{ name: 'chats-item-item_id', params: { item_id: item.id } }">
            <Box :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
            <div>Voir l'objet</div>
          </NuxtLink>
        </DropdownMenuItem>

      </DropdownMenu>

    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <ChatMessagesList :src="chatMessagesStore" ref="main" class="app-content" />
    </main>

    <ChatMessageInput v-model="chatMessageInput" @submit="submitMessage" />

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.ChatMessageInput {
  position: absolute;
  bottom: 80px;
  left: 0;
  right: 0;
}
</style>
