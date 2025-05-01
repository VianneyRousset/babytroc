<script setup lang="ts">
// get item ID from route
const route = useRoute();
const itemId = Number.parseInt(route.params.item_id as string); // TODO avoid this hack

const { currentTab } = useTab();

// goto tab main page if invalid itemId
if (isNaN(itemId)) navigateTo(`/${currentTab}`)

// get main header bar height to offset content
const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(
	useTemplateRef("main-header"),
);

// query item, me, saved items and liked items
const { state: item, asyncStatus: itemAsyncStatus } = useItemQuery(itemId);
const { state: me } = useMeQuery();
const { state: savedItems } = useSavedItemsQuery();
const { state: likedItems, asyncStatus: likedAsyncStatus } =
	useLikedItemsQuery();
const { state: loanRequests } = useBorrowingsLoanRequestsListQuery({active: true});
</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <AppBack />
      <h1 :title="item.data?.name">{{ item.data?.name }}</h1>

      <!-- Dropdown menu -->
      <ItemDropdownMenu v-if="item.data && savedItems.data" :item="item.data" :saved-items="savedItems.data" />

    </AppHeaderBar>

    <!-- Main content -->
    <main ref="main" class="app-content page">

      <!-- Gallery -->
      <ItemPresentation v-if="item.data" :item="item.data!"
        :item-async-status="itemAsyncStatus" :me="me.data" :liked-items="likedItems.data ?? []"
        :liked-async-status="likedAsyncStatus" :loan-requests="loanRequests.data ?? []" />
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
