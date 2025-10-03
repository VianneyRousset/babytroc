<script setup lang="ts">
// get item ID from route
const route = useRoute()
const itemId = Number.parseInt(route.params.item_id as string) // TODO avoid this hack
const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(itemId)) navigateTo(`/${currentTab}`)

// query item
const { item, loading } = useItem({ itemId })

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
          <div class="description">
            <h1>{{ item.name }}</h1>
            <p>{{ item.description }}</p>
          </div>
          <ItemInfoBox :item="item" />
          <ItemOwner
            :item="item"
            :chevron="true"
          />
          <h2>Informations</h2>
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
          <ItemImagesGallery
            :item="item"
            wide
          />
          <section
            class="h golden-left"
            style="gap: 2em;"
          >
            <div class="name-description">
              <h1>{{ item.name }}</h1>
              <p>{{ item.description }}</p>
              <ItemAge
                :item="item"
                :lowercase="true"
                prefix="Convient à des enfants "
              />
            </div>
            <div class="v">
              <ItemInfoBox :item="item" />
              <ItemOwner
                :item="item"
                :chevron="true"
              />
              <ItemRequestButton :item="item" />
            </div>
          </section>
          <section>
            <h2>Régions</h2>
            <div class="h golden-left">
              <ItemRegionsList :item="item" />
              <ItemRegionsMap :item="item" />
            </div>
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

  .name-description {
    h1 {
      margin: 0;
    }
  }

  section {
    font-size: clamp(0.6em, 2vw, 1em);

    .ItemAge {
      color: $neutral-400;
      font-style: italic;
    }

    .ItemRegionsList {
      font-size: clamp(0.6em, 1.4vw, 0.8em);
      padding: 2em 0;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
