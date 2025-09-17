<script setup lang="ts">
// get item ID from route
const route = useRoute()
const itemId = Number.parseInt(route.params.item_id as string) // TODO avoid this hack

const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(itemId)) navigateTo(`/${currentTab}`)

// query item, me, saved items and liked items
const { item, error, loading } = useItem({ itemId })
const { state: me } = useMeQuery()
const { state: loanRequests } = useBorrowingsLoanRequestsListQuery({ active: true })

// auth
const { loggedIn } = useAuth()
</script>

<template>
  <AppPage>
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1 :title="item?.name">
        {{ item?.name }}
      </h1>

      <!-- Dropdown menu -->
      <ItemDropdownMenu
        v-if="loggedIn === true && item"
        :item="item"
      />
    </template>

    <Panel v-if="item">
      <!-- Gallery -->
      <section>
        <ItemImagesGallery :item="item" />
        <h2>
          {{ item.name }}
        </h2>
      </section>

      <!-- Availability and likes count -->
      <section>
        <ItemAvailability :available="item.available" />
        <ItemLike
          :item="item"
          :disabled="false"
        />
      </section>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
