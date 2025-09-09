<script setup lang="ts">
// get item ID from route
const route = useRoute()
const itemId = Number.parseInt(route.params.item_id as string) // TODO avoid this hack

const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(itemId)) navigateTo(`/${currentTab}`)

// query item, me, saved items and liked items
const { state: item, asyncStatus: itemAsyncStatus } = useItemQuery(itemId)
const { state: me } = useMeQuery()
const { state: savedItems } = useSavedItemsQuery()
const { state: likedItems, asyncStatus: likedAsyncStatus } = useLikedItemsQuery()
const { state: loanRequests } = useBorrowingsLoanRequestsListQuery({ active: true })

// auth
const { loggedIn } = useAuth()
</script>

<template>
  <AppPage :hide-on-scroll="true">
    <!-- Header bar -->
    <template #header>
      <AppBack />
      <h1 :title="item.data?.name">
        {{ item.data?.name }}
      </h1>

      <!-- Dropdown menu -->
      <ItemDropdownMenu
        v-if="loggedIn === true && item.data && savedItems.data"
        :item="item.data"
        :saved-items="savedItems.data"
      />
    </template>

    <!-- Main content -->
    <main
      class="app-content page"
    >
      <!-- Gallery -->
      <ItemPresentation
        v-if="item.data"
        :item="item.data!"
        :item-async-status="itemAsyncStatus"
        :me="me.data"
        :liked-items="likedItems.data ?? []"
        :liked-async-status="likedAsyncStatus"
        :loan-requests="loanRequests.data ?? []"
      />
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
