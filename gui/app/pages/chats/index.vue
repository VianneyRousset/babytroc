<script setup lang="ts">
// const numbers: Array<number> = await useApiPaginatedQuery('/v1/items', { key: ['items'] })
const { data, loadMore } = useApiPaginatedQuery('/v1/items', { key: ['items'] })

loadMore()

// const test1 = await useApiPaginatedQuery('/v1/auth/login', { key: ['items'] })
// const test2 = useApiPaginatedQuery('/v1/auth/available', { key: ['items'] })
// const test3 = useApiPaginatedQuery('/v1/utils/regions', { key: ['items'] })
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
      {{ data }}
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
