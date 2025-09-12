<script setup lang="ts">
import { Filter, LayoutGrid, Grid3x3 } from 'lucide-vue-next'
import { AppPage } from '#components'

const device = useDevice()

// item filters
const { filters, isDefault: isFiltersDefault, reset: resetFilters, loadFiltersFromQueryParams, dumpFiltersAsQueryParams } = useItemFilters()

// synced store and route query params
const { queryParams } = useItemExploreQueryParams()

// update filters when route query params changes
watch(queryParams, newQueryParams => loadFiltersFromQueryParams(newQueryParams), { immediate: true })

// query items
const { items, error, loading, loadMore } = useItemExplore({ queryParams: queryParams! })

// filters are applied by updating the route query params
const applyFilters = () => (queryParams.value = dumpFiltersAsQueryParams())

const openItem = (itemId: number) => navigateTo(`/explore/item/${itemId}`)

// dense layout
const dense = ref(false)

// filters drawer open state
const filtersDrawerOpen = ref(false)
</script>

<template>
  <AppPage
    saved-scroll="page-explore"
    :hide-bar-on-scroll="true"
    :infinite-scroll="true"
    :infinite-scroll-distance="1800"
    @more="loadMore"
  >
    <!-- Header bar (mobile only) -->
    <template
      v-if="device.isMobile"
      #header
    >
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

    <!-- Filters drawer -->
    <aside>
      <Teleport to="body">
        <Overlay
          v-model="filtersDrawerOpen"
        />
        <ItemExploreFiltersDrawer
          v-model:open="filtersDrawerOpen"
          v-model:filters="filters"
          :is-default="isFiltersDefault"
          @close="applyFilters"
          @reset="resetFilters"
        />
      </Teleport>
    </aside>

    <!-- Item cards -->
    <main>
      <ItemCardsCollection
        :items="items"
        :dense="dense"
        :loading="loading"
        :error="error"
        @select="openItem"
      />
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.floating-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.6em;
  position: absolute;
  right: 0.6em;
  top: calc(var(--app-header-bar-height) + 0.6em);
}
</style>
