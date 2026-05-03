<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

const { loans, isLoading, error, loadMore } = useMeBorrowings({ active: false })
</script>

<template>
  <AppPage
    logged-in-only
    infinite-scroll
    :infinite-scroll-distance="1200"
    @more="loadMore"
  >
    <!-- Header bar -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Anciens emprunts</h1>
    </template>

    <!-- Main content -->
    <main>
      <Panel>
        <ListError v-if="error">
          Une erreur est survenue.
        </ListError>
        <ListEmpty v-else-if="!isLoading && loans?.length === 0">
          Aucun ancien emprunt
        </ListEmpty>
        <SlabList v-else>
          <LoanSlab
            v-for="loan in loans"
            :key="`loan${loan.id}`"
            :loan="loan"
            :target="`/explore/item/${loan.item.id}`"
            chevron
          />
        </SlabList>
        <ListLoader v-if="isLoading" />
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main :deep(.content) {
  .SlabList {
    background: $bg-surface;
    border-radius: $radius-md;
    box-shadow: $shadow-sm;
    overflow: hidden;
  }
}
</style>
