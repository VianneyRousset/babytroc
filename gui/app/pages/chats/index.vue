<script setup lang="ts">
import { MessageSquare, LockKeyholeOpen } from "lucide-vue-next";

const { chats } = useChats();
const { data: me } = useMeQuery();
const { loggedIn, loggedInStatus, loginRoute } = useAuth();

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
      <!-- Loader when not knowing if logged in -->
      <div v-if="loggedInStatus === 'pending'" class="app-content flex-column-center">
        <Loader />
      </div>

      <!-- Not logged in prompt -->
      <div v-else-if="loggedIn === false" class="app-content flex-column-center">
        <div class="lock">
          <LockKeyholeOpen :size="48" :strokeWidth="3" :absoluteStrokeWidth="true" />
          <div>Vous n'êtes pas connecté</div>
          <TextButton aspect="outline" @click="navigateTo(loginRoute)">Se connecter</TextButton>
        </div>
      </div>

      <!-- Logged in: show the chats list -->
      <SlabList v-else-if="loggedIn ===true && chats && me" class="app-content">
        <NuxtLink v-for="chat in chats" :to="`/chats/${chat.id}`" :id="`chat-${chat.id}`"
          :key="`chat-${chat.id}`" class="reset-link">
          <ChatSlab :chat="chat" :me="me" :key="`${chat.id}`" />
          <!-- TODO add empty -->
        </NuxtLink>
        <ListEmpty v-if="chats.length === 0">Vous n'avez pas encore de message.</ListEmpty>
      </SlabList>

    </main>

  </div>
</template>


<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.lock {
  @include flex-column-center;
  gap: 1rem;
  color: $neutral-800;
}

.app-content {
  .ChatSlab {
    border-bottom: 1px solid $neutral-200;
  }
}
</style>
