<script setup lang="ts">
import { MessageCircleQuestion, Archive } from 'lucide-vue-next'

definePageMeta({
  layout: 'me',
})

const { loans, isLoading, error, loadMore } = useMeBorrowings({ active: true })
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
      <h1>Mes emprunts</h1>
    </template>

    <!-- Main content -->
    <main>
      <Panel>
        <!-- Active borrowings -->
        <section>
          <h2>Emprunts actifs</h2>
          <ListError v-if="error">
            Une erreur est survenue.
          </ListError>
          <ListEmpty v-else-if="!isLoading && loans?.length === 0">
            Aucun emprunt actif
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

        <!-- Links to requests and archived -->
        <section>
          <SlabList>
            <Slab
              :icon="MessageCircleQuestion"
              target="/me/borrowings/requests"
              chevron
            >
              Demandes d'emprunts
            </Slab>
            <Slab
              :icon="Archive"
              target="/me/borrowings/archived"
              chevron
            >
              Anciens emprunts
            </Slab>
          </SlabList>
        </section>
      </Panel>
    </main>
  </AppPage>
</template>
