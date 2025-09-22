<script setup lang="ts">
const { data: loans } = useLoansListQuery()
</script>

<template>
  <AppPage>
    <!-- Header bar -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Mes prêts</h1>
    </template>

    <!-- Main content -->
    <Panel>
      <section>
        <h2>Actifs</h2>
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
    </Panel>
  </AppPage>
</template>
