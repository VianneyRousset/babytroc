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
const { items, error, isLoading, loadMore } = useItemExplore({ queryParams })

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

// apply filter when drawer is closed
watch(filtersDrawerOpen, (newState, oldState) => {
  if (!newState && oldState)
    applyFilters()
})
</script>

<template>
  <AppPage
    saved-scroll="page-explore"
    hide-bar-on-scroll
    infinite-scroll
    with-header
    :infinite-scroll-distance="1800"
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
      <ConditionalDrawer
        v-model="filtersDrawerOpen"
        position="right"
        :drawer="drawerMode"
      >
        <Panel>
          <ItemExploreFilters
            v-model="filters"
            :size="device.isMobile ? 'large' : 'normal'"
          />
          <template
            v-if="drawerMode"
            #header
          >
            <IconButton
              class="Toggle"
              @click="() => { filtersDrawerOpen = false }"
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
          <template
            v-else
            #header
          >
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
        </Panel>
      </ConditionalDrawer>
    </template>

    <template #desktop>
      <AppHeaderDesktop>
        <template
          v-if="drawerMode"
          #buttons-right
        >
          <ToggleIcon
            v-model="filtersDrawerOpen"
            :active="!isFiltersDefault"
            class="filter"
          >
            <Filter
              :size="32"
              :stroke-width="1.33"
            />
          </ToggleIcon>
        </template>
        <h1>Trouvez ici les objets que vous voulez emprunter</h1>
        <SearchInput
          v-model="filters.words"
          @submit="applyFilters"
        />
      </AppHeaderDesktop>
    </template>

    <!-- Item cards -->
    <main>
      <Panel>
        <ItemCardsCollection
          :items="items"
          :dense="dense"
          :loading="isLoading"
          :error="error != null"
          @select="openItem"
        />
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.AppHeaderDesktop {
  font-size: clamp(0.5em, 1.5vw, 1em);
  h1 {
    text-align: center;
  }
  .SearchInput {
    width: 80%;
  }
}

.ToggleIcon.filter {
  margin-right: 4em;
  color: $neutral-400;
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
