<script setup lang="ts">
import { MessageCircleQuestion, Archive } from 'lucide-vue-next'

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const { data: loans } = useBorrowingsListQuery()
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>Mes emprunts</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main class="app-content">
      <!-- Active borrowings -->
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
      <!-- Requests and ended borrwoings -->
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
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
