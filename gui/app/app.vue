<script setup lang="ts">
const { loggedIn } = useAuth()

let websocket: WebSocket | null = null

const { addMessage } = useChats()

watch(loggedIn, (state) => {
  if (state === true) {
    // websocket uri
    const loc = window.location
    const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
    const uri = `${proto}//${loc.host}/api/v1/me/websocket`

    // open websocket and attach event listener
    websocket = new WebSocket(uri)

    websocket.addEventListener('message', (event) => {
      const wsMessage = JSON.parse(event.data)

      if (
        ['new_chat_message', 'updated_chat_message'].includes(wsMessage.type)
      ) {
        addMessage(wsMessage.message)
      }
    })
  }
  else {
    if (websocket != null) {
      websocket.close()
      websocket = null
    }
  }
})

// deduce transition to use base on platform and navigation direction
const device = useDevice()
const { direction, resetDirection } = useNavigation()
const transitionName = computed(() => device.isMobile ? `page-slide-${unref(direction)}` : 'fade')
const transitionMode = computed(() => device.isMobile ? 'in-out' : 'out-in')

const pageActiveTransition = ref<boolean>(false)
provide<Ref<boolean>>('page-active-transition', pageActiveTransition)

function onBeforeLeave() {
}

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
        onBeforeLeave,
        onAfterEnter,
      }"
    />
  </NuxtLayout>
</template>
