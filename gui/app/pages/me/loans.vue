<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

const { loans, isLoading, error, loadMore } = useMeLoans({ active: true })
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
      <h1>Mes prêts</h1>
    </template>

    <!-- Main content -->
    <main>
      <Panel>
        <section>
          <h2>Prêts actifs</h2>
          <ListError v-if="error">
            Une erreur est survenue.
          </ListError>
          <ListEmpty v-else-if="!isLoading && loans?.length === 0">
            Aucun prêt actif
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
        </section>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main :deep(.content) {
  section {
    display: flex;
    flex-direction: column;
    gap: $space-2;

    h2 {
      color: $text-secondary;
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0 $space-4;
    }

    .SlabList {
      background: $bg-surface;
      border-radius: $radius-md;
      box-shadow: $shadow-sm;
      overflow: hidden;
    }
  }
}
</style>
