<script setup lang="ts">
definePageMeta({
	layout: "saved",
});

const { items, error, isLoading, loadMore } = useSavedItems();
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
      <h1>Mes Favorits</h1>
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
main {
  .Panel {
    :deep(.content:empty),
    :deep(.content > .ItemCardsCollection:empty) {
      @include flex-column-center;
      padding: $space-16;
      color: $text-tertiary;
    }
  }
}
</style>
