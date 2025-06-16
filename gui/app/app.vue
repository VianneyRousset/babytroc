<script setup lang="ts">
const { loggedIn } = useAuth()

let websocket: WebSocket | null = null

const { setMessage } = useChats()
const route = useRoute()

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

const visible = computed(() => !([
  '/newitem',
  '/me/account/pending-validation',
  '/me/account/reset-password',
  '/me/account/validate',
].some(r => route.path.startsWith(r))))
</script>

<template>
  <div>
    <NuxtPage />
    <AppFooterBar v-if="visible" />
  </div>
</template>

<style></style>
