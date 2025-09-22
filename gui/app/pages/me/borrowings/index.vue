<script setup lang="ts">
import { MessageCircleQuestion, Archive } from 'lucide-vue-next'

const { data: loans } = useBorrowingsListQuery()
</script>

<template>
  <AppPage>
    <!-- Header bar -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Mes emprunts</h1>
    </template>

    <!-- Main content -->
    <Panel>
      <!-- Active borrowings -->
      <section>
        <h2>Emprunts actifs</h2>
        <SlabList>
          <NuxtLink
            v-for="loan in loans"
            :key="`loan${loan.id}`"
            :to="{ name: 'home-item-item_id', params: { item_id: loan.item.id } }"
          >
            <LoanSlab :loan="loan" />
          </NuxtLink>
        </SlabList>
      </section>

      <!-- Requests and ended borrwoings -->
      <section>
        <h2>Demandes d'emprunts</h2>
        <SlabList>
          <NuxtLink to="/me/borrowings/requests">
            <MeSlab>
              Demandes d'emprunts
              <template #image>
                <MessageCircleQuestion
                  :size="32"
                  :stroke-width="2"
                />
              </template>
            </MeSlab>
          </NuxtLink>
          <NuxtLink to="/me/borrowings/archived">
            <MeSlab>
              Anciens emprunts
              <template #image>
                <Archive
                  :size="32"
                  :stroke-width="2"
                />
              </template>
            </MeSlab>
          </NuxtLink>
        </SlabList>
      </section>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
