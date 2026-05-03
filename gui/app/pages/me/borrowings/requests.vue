<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

const { loans: requests, isLoading, error, loadMore } = useMeBorrowingRequests()
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
      <h1>Demandes d'emprunts</h1>
    </template>

    <!-- Main content -->
    <main>
      <Panel>
        <ListError v-if="error">
          Une erreur est survenue.
        </ListError>
        <ListEmpty v-else-if="!isLoading && requests?.length === 0">
          Aucune demande d'emprunt
        </ListEmpty>
        <SlabList v-else>
          <LoanRequestSlab
            v-for="request in requests"
            :key="`request${request.id}`"
            :loan-request="request"
            :target="`/explore/item/${request.item.id}`"
            chevron
          />
        </SlabList>
        <ListLoader v-if="isLoading" />
      </Panel>
    </main>
  </AppPage>
</template>
