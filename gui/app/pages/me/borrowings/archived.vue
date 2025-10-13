<script setup lang="ts">
const { loans } = useMeBorrowings()
</script>

<template>
  <AppPage>
    <!-- Header bar -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Mes anciens emprunts</h1>
    </template>

    <!-- Main content -->
    <Panel>
      <!-- Borrowing requests -->
      <SlabList>
        <NuxtLink
          v-for="loan in loans"
          :key="`loan${loan.id}`"
          :to="{ name: 'home-item-item_id', params: { item_id: loan.item.id } }"
        >
          <LoanSlab :loan="loan" />
        </NuxtLink>
      </SlabList>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
