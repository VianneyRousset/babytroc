<script setup lang="ts">
import { Menu, MessageSquare } from 'lucide-vue-next'
// get chat ID from route
const route = useRoute()
const chatId = computed<string | undefined>(() => {
  const _chatId = String(route.params.chat_id)
  return verifyChatIdFormat(_chatId) ? _chatId : undefined
})
useAuth({ fallbackRoute: '/chats' })

const { me } = useMe()

const { narrowWindow } = useNarrowWindow()
const drawerMode = computed<boolean>(() => unref(narrowWindow))

// chats drawer open state
const chatsDrawerOpen = ref(false)
</script>

<template>
  <AppPage logged-in-only>
    <!-- Header bar (mobile only) -->
    <template
      v-if="chatId == null"
      #mobile-header-bar
    >
      <MessageSquare
        :size="32"
        :stroke-width="2"
      />
      <h1>Chats</h1>
    </template>
    <template
      v-else
      #mobile-header-bar
    >
      <AppBack />
      <h1>Chats</h1>
    </template>

    <!-- Chats (desktop version) -->
    <template #desktop>
      <main class="desktop">
        <ChatView
          v-if="chatId && me"
          :chat-id="chatId"
          :me="me"
        />
        <FloatingToggle
          v-model="chatsDrawerOpen"
        >
          <Menu
            :size="24"
            :stroke-width="1.33"
          />
        </FloatingToggle>
        <ConditionalDrawerOverlay
          :model-value="chatsDrawerOpen || chatId == null"
          position="left"
          :page="false"
          :drawer="drawerMode"
          @update:model-value="v => chatId != null && (chatsDrawerOpen = (v == true))"
        >
          <ChatsList :active="chatId" />
        </ConditionalDrawerOverlay>
      </main>
    </template>

    <!-- Chats (mobile version) -->
    <template #mobile>
      <main
        v-if="chatId == null"
      >
        <ChatsList />
      </main>
      <main
        v-else
        class="mobile"
      >
        <ChatView
          v-if="chatId && me"
          :chat-id="chatId"
          :me="me"
        />
      </main>
    </template>
  </AppPage>
</template>

<style scoped lang="scss">
.AppPage {
  @include flex-column;
  flex: 1; 
  min-height: 0;
  align-items: stretch;
}

main.mobile {
  height: calc(100% - var(--app-header-bar-height) - var(--app-footer-bar-height));

  .ChatView {
    height: 100%;
  }
}

main.desktop {
  display: flex;
  flex-direction: row-reverse !important;
  justify-content: flex-end;
  margin: 2em;
  flex: 1;
  min-height: 0;
  position: relative;

  border-radius: 1em;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  border: 1px solid $neutral-200;
  overflow: hidden;

  .FloatingToggle {
    position: absolute;
    top: 1em;
    left: 1em;
    background: white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }

  & > .ConditionalDrawerOverlay {
    @include flex-column;
    flex: 1;
    max-width: 500px;
    border-right: 1px solid $neutral-200;
    & > * {
      width: 100%;
    }
  }

  & > .ChatView {
    flex: 1;
  }
}
</style>
