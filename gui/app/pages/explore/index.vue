<script setup lang="ts">
/**
 * Explore items page.
 *
 * Filtering:
 *
 *      ┌────────────────────────────┐
 *      ▼                            │
 *    filters ──applyFilters()─► queryParams ─► Queried items
 *      ▲
 *      └─► <input>
 **/

import { Filter, LayoutGrid, Grid3x3, ArrowLeft, Repeat } from 'lucide-vue-next'
import { AppPage } from '#components'
import { isEqual, cloneDeep } from 'lodash'

const device = useDevice()

// item filters
const { filters, isDefault: isFiltersDefault, reset: resetFilters, loadFiltersFromQueryParams, dumpFiltersAsQueryParams } = useItemFilters()

// synced store and route query params
const { queryParams } = useItemExploreQueryParams()

// update filters when route query params changes
watch(queryParams, newQueryParams => loadFiltersFromQueryParams(newQueryParams), { immediate: true })

// query items
const { items, error, loading, loadMore } = useItemExplore({ queryParams })

// filters are applied by updating the route query params
const applyFilters = () => (queryParams.value = dumpFiltersAsQueryParams())

const openItem = (itemId: number) => navigateTo(`/explore/item/${itemId}`)

// dense layout
const dense = ref(false)

const { narrowWindow } = useNarrowWindow()
const drawerMode = computed<boolean>(() => device.isMobile || unref(narrowWindow))

// filters drawer open state
const filtersDrawerOpen = ref(false)

// in panel mode (no drawer), the filters updates the queryparams without having to trigger applyFilters() manually
watch(computed(() => cloneDeep(unref(filters))), (newFilters, oldFilters) => {
  // skip if no change or not in panel model
  if (unref(drawerMode) || isEqual(newFilters, oldFilters))
    return

  setTimeout(applyFilters, 500)
}, { deep: true })
</script>

<template>
  <AppPage
    saved-scroll="page-explore"
    :hide-bar-on-scroll="true"
    :infinite-scroll="true"
    :infinite-scroll-distance="1800"
    :drawer-right="filtersDrawerOpen"
    @more="loadMore"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <SearchInput
        v-model="filters.words"
        @submit="applyFilters"
      />
      <!-- Floating buttons -->
      <div class="floating-buttons">
        <FloatingToggle
          v-model="filtersDrawerOpen"
          :active="!isFiltersDefault"
        >
          <Filter
            :size="24"
            :stroke-width="2"
          />
        </FloatingToggle>
        <FloatingToggle v-model="dense">
          <transition
            name="fade"
            mode="out-in"
          >
            <LayoutGrid
              v-if="dense"
              :size="24"
              :stroke-width="2"
            />
            <Grid3x3
              v-else
              :size="24"
              :stroke-width="2"
            />
          </transition>
        </FloatingToggle>
      </div>
    </template>

    <!-- Filters panel (larger screen only) -->
    <template #left>
      <PanelOrDrawer
        v-model="filtersDrawerOpen"
        position="right"
        :mode="drawerMode ? 'drawer' : 'panel'"
      >
        <ItemExploreFilters
          v-model="filters"
          :size="device.isMobile ? 'large' : 'normal'"
        />
        <template #header-panel>
          <h1>Filtres</h1>
          <IconButton
            :disabled="isFiltersDefault"
            @click="resetFilters"
          >
            <Repeat
              :size="24"
              :stroke-width="2"
            />
          </IconButton>
        </template>
        <template #header-drawer>
          <IconButton
            class="Toggle"
            @click="() => { applyFilters(); filtersDrawerOpen = false }"
          >
            <ArrowLeft
              :size="32"
              :stroke-width="2"
            />
          </IconButton>
          <h1>Filtres</h1>
          <IconButton
            :disabled="isFiltersDefault"
            @click="resetFilters"
          >
            <Repeat
              :size="24"
              :stroke-width="2"
            />
          </IconButton>
        </template>
      </PanelOrDrawer>
    </template>

    <template #desktop-header>
      <div class="desktop-header">
        <div>Trouvez ici les objets que vous voulez emprunter</div>
        <SearchInput
          v-model="filters.words"
          @submit="applyFilters"
        />
      </div>
    </template>

    <!-- Item cards -->
    <ItemCardsCollection
      :items="items"
      :dense="dense"
      :loading="loading"
      :error="error"
      @select="openItem"
    />
  </AppPage>
</template>

<style scoped lang="scss">
.desktop-header {
  @include flex-column;
  padding: 1em;
  gap: 1em;

  div:first-child {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 1.2em;
    font-style: italic;
    color: $neutral-600;
    padding: 1em;
  }
  .SearchInput {
    width: 80%;
  }
}

.floating-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.6em;
  position: absolute;
  right: 0.6em;
  top: calc(var(--app-header-bar-height) + 0.6em);
}
</style>
