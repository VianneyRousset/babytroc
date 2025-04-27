<script setup lang="ts">
import { MessageSquare } from "lucide-vue-next";

const { data: chatsPages, status: chatsStatus } = useChatsListQuery();
const { data: me } = useMeQuery();

// get main header bar height to offset content
const { height: mainHeaderHeight } = useElementSize(
	useTemplateRef("main-header"),
);
</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <MessageSquare :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <h1>Messages</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <SlabList v-if="chatsPages.data && me" class="app-content">
        <NuxtLink v-for="chat in chatsPages.data" :to="`/chats/${chat.id}`" :id="`chat-${chat.id}`"
          :key="`chat-${chat.id}`" class="reset-link">
          <ChatSlab :chat="chat" :me="me" :key="`${chat.id}`" />
          <!-- TODO add empty -->
        </NuxtLink>
        <ListEmpty v-if="chatsPages.data && chatsPages.data.length === 0">Vous n'avez pas encore de message.</ListEmpty>
      </SlabList>
    </main>

  </div>
</template>


<style scoped lang="scss">
.app-content {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.app-content {
  @include flex-column;
  gap: 0;
  flex-grow: 1;
  overflow-y: scroll;
  align-items: stretch;

  .ChatSlab {
    border-bottom: 1px solid $neutral-200;
  }
}
</style>
