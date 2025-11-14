<script setup lang="ts">
import { Heart } from 'lucide-vue-next'

definePageMeta({
  layout: 'saved',
})

const { items, error, isLoading, loadMore } = useSavedItems()
</script>

<template>
  <AppPage
    logged-in-only
    with-header
    :max-width="1000"
    infinite-scroll
    :infinite-scroll-distance="1800"
    @more="loadMore"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <Heart
        :size="32"
        :stroke-width="2"
      />
      <h1>Favorits</h1>
    </template>

    <!-- Header (desktop only) -->
    <template #desktop>
      <AppHeaderDesktop>
        <h1>Mes Favorits</h1>
      </AppHeaderDesktop>
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
