<script setup lang="ts">
// get item ID from route
const route = useRoute()
const itemId = Number.parseInt(route.params.item_id as string) // TODO avoid this hack
const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(itemId)) navigateTo(`/${currentTab}`)

// query item, me, saved items and liked items
const { item, loading } = useItem({ itemId })
const { state: me } = useMeQuery()
const { state: loanRequests } = useBorrowingsLoanRequestsListQuery({ active: true })

// auth
const { loggedIn } = useAuth()

const device = useDevice()
</script>

<template>
  <AppPage :max-width="1000">
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

    <!-- Mobile page -->
    <template #mobile>
      <main>
        <Panel v-if="item">
          <ItemImagesGallery :item="item" />
          <ItemInfoBox :item="item" />
          <div class="description">
            <h1>{{ item.name }}</h1>
            <p>{{ item.description }}</p>
          </div>
          <ItemMinitable
            v-if="device.isMobile"
            :item="item"
          />
          <ItemRegionsMap :item="item" />
          <ItemRequestButton :item="item" />
        </Panel>
        <LoadingAnimation v-else-if="loading" />
      </main>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
      <main>
        <Panel
          v-if="item"
          class="desktop"
        >
          <section class="h golden-right">
            <!-- Gallery -->
            <ItemImagesGallery :item="item" />
            <div class="description">
              <h1>{{ item.name }}</h1>
              <p>{{ item.description }}</p>
              <ItemAge
                :item="item"
                :lowercase="true"
                prefix="Convient à des enfants "
              />
              <ItemInfoBox :item="item" />
              <ItemRequestButton :item="item" />
            </div>
          </section>
          <section class="h golden-left">
            <ItemRegionsList :item="item" />
            <ItemRegionsMap :item="item" />
          </section>
        </Panel>
        <LoadingAnimation v-else-if="loading" />
      </main>
    </template>
  </AppPage>
</template>

<style scoped lang="scss">
:deep(.Panel.desktop .content) {

  gap: 2em;

  section {
    font-size: clamp(0.6em, 2vw, 1em);

    &:not(:first-child){
      padding: 0 1em;
    }

    .ItemAge {
      color: $neutral-400;
      font-style: italic;
    }

    .ItemRegionsList {
      font-size: clamp(0.6em, 1.4vw, 0.8em);
      padding: 2em 0;
    }

    .ItemInfoBox {
      padding: 2em 0;
    }

    .ItemRequestButton {
      grid-area: request;
      align-self: start;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
