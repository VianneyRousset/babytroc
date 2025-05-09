<script setup lang="ts">

const { $toast } = useNuxtApp();
const { loggedIn } = useAuth();
const route = useRoute();

let websocket: WebSocket | null = null;

const { setMessage } = useChats();

watch(loggedIn, (state) => {

  if (state === true) {

    // websocket uri
    const loc = window.location;
    const proto = loc.protocol === "https:" ? "wss:" : "ws:";
    const uri = `${proto}//${loc.host}/api/v1/me/websocket`;

    // open websocket and attach event listener
    websocket = new WebSocket(uri);

    websocket.addEventListener("message", (event) => {

      const wsMessage = JSON.parse(event.data);
      
      if (["new_chat_message", "updated_chat_message"].includes(wsMessage.type)) {
        setMessage(wsMessage.message);
      }
      
    });    

    
  } else {
    if (websocket != null) {
      websocket.close();
      websocket = null;
    }
  }
  
});

</script>

<template>
  <div>
    <NuxtPage />
    <AppFooterBar />
  </div>
</template>

<style></style>
