<script setup lang="ts">
const { loggedIn } = useAuth()

let websocket: WebSocket | null = null

const { setMessage } = useChats()

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
        setMessage(wsMessage.message)
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

// deduce transition to use base on navigation direction
const { direction, resetDirection } = useNavigation()
const transitionName = computed(() => `page-slide-${unref(direction)}`)

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
        mode: 'in-out',
        onBeforeLeave,
        onAfterEnter,
      }"
    />
  </NuxtLayout>
</template>
