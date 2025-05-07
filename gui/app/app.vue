<script setup lang="ts">

const { $toast } = useNuxtApp();
const { loggedIn } = useAuth();
const route = useRoute();

let websocket: WebSocket | null = null;

const {addMessage} = useChats();

watch(loggedIn, (state) => {

  if (state === true) {

    // websocket uri
    const loc = window.location;
    const proto = loc.protocol === "https:" ? "wss:" : "ws:";
    const uri = `${proto}//${loc.host}/api/v1/me/websocket`;

    console.log("open websocket", uri);
  
    // open websocket and attach event listener
    websocket = new WebSocket(uri);

    websocket.addEventListener("message", (event) => {
      console.log("websocket:", event.data);

      const wsMessage = JSON.parse(event.data);
      
      if (wsMessage.type === "new_chat_message") {
        console.log("addMessage because new_caht_mesage");
        addMessage(wsMessage.message);
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
