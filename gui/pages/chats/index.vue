<script setup lang="ts">

import { MessageSquare } from 'lucide-vue-next';

const chatsStore = useChatsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

</script>

<template>

  <!-- Header bar -->
  <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
    <MessageSquare :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
    <h1>Messages</h1>
  </AppHeaderBar>

  <!-- Main content -->
  <main>
    <ChatSlabsList :src="chatsStore" target="home" ref="main" class="app-content" />
  </main>

</template>


<style scoped lang="scss">
.app-content {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
