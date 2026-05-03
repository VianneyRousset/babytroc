<script setup lang="ts">
import { MessageCircleQuestion, Archive } from 'lucide-vue-next'

definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'Mes emprunts',
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
