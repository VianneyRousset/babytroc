<script setup lang="ts">
definePageMeta({
  layout: 'saved',
})

const { items, error, isLoading, loadMore } = useSavedItems()
</script>

<template>
  <AppPage
    with-header
    :max-width="1000"
    infinite-scroll
    :infinite-scroll-distance="1800"
    @more="loadMore"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <h1>Favorits</h1>
    </template>

    <!-- Item cards -->
    <main>
      <Panel>
        <ItemCardsCollection
          :items="items"
          :loading="isLoading"
          :error="error != null"
          :target="itemId => `/explore/item/${itemId}`"
        />
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
