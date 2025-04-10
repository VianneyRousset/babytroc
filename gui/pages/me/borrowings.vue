<script setup lang="ts">

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

const { data: loans } = useBorrowingsListQuery();

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

function openItem(itemId: number) {
  routeStack.amend(router.resolve({ ...route, hash: `#item${itemId}` }).fullPath);
  return navigateTo(`/home/item/${itemId}`);
}

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
      <h2>Actifs</h2>
      <SlabList>
        <NuxtLink v-for="loan in loans" :to="{ name: 'home-item-item_id', params: { item_id: loan.item.id } }">
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
