<script setup lang="ts">
const { loggedIn } = useAuth()
const { addMessage } = useChats()

// add new chat messages from websocket to chats if logged in
useLiveMessage(
  'new_chat_message',
  wsMessage => addMessage(wsMessage.message), {
    enabled: () => unref(loggedIn) === true,
  },
)

// update chat messages from websocket to chats if logged in
useLiveMessage(
  'updated_chat_message',
  wsMessage => addMessage(wsMessage.message), {
    enabled: () => unref(loggedIn) === true,
  },
)

// deduce transition to use base on platform and navigation direction
const device = useDevice()
const { direction, resetDirection } = useNavigation()
const transitionName = computed(() => device.isMobile ? `page-slide-${unref(direction)}` : 'fade')
const transitionMode = computed(() => device.isMobile ? 'in-out' : 'out-in')

const pageActiveTransition = ref<boolean>(false)
provide<Ref<boolean>>('page-active-transition', pageActiveTransition)

function onAfterEnter() {
  resetDirection()
}
</script>

<template>
  <NuxtLayout>
    <NuxtPage
      :transition="{
        name: transitionName,
        mode: transitionMode,
        onAfterEnter,
      }"
    />
  </NuxtLayout>
</template>
