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
