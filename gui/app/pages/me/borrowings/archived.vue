<script setup lang="ts">
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
      <h1>Mes anciens emprunts</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main class="app-content">
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
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
