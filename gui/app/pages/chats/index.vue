<script setup lang="ts">
</script>

<template>
  <AppPage hide-bar-on-scroll>
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      Chats
    </template>

    <template #mobile>
      Mobile chats
    </template>

    <template #left>
      <ChatsList />
    </template>

    <template #desktop>
      <AppHeaderDesktop />
    </template>

    <!-- Item cards -->
    <main>
      <Panel />
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
