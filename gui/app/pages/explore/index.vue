<script setup lang="ts">
import { Filter } from 'lucide-vue-next'

const filtersDrawerOpen = ref(false)

const { queryParams } = useMirrorItemQueryParamsAndRouteQueryParams()

// query items
const {
  items,
  error,
  loading,
  loadMore,
  canLoadMore,
} = useItemExplore({ queryParams })

// item filters
const { filters, loadFiltersFromQueryParams, dumpFiltersAsQueryParams } = useItemFilters()

watch(queryParams, _queryParams => loadFiltersFromQueryParams(_queryParams), { immediate: true })

const applyFilters = () => queryParams.value = dumpFiltersAsQueryParams()

function openItem(itemId: number) {
  const route = useRoute()
  const router = useRouter()
  const routeStack = useRouteStack()
  routeStack.amend(
    router.resolve({ ...route, hash: `#item${itemId}` }).fullPath,
  )
  return navigateTo(`/home/item/${itemId}`)
}

const searchInput = ref('')
const isFilterActive = ref(false)

/*
useInfiniteScroll(
  document,
  async () => {
    await loadMore()
  },
  {
    canLoadMore: () => !unref(itemsPages).end && unref(itemsStatus) !== 'error',
    distance: 1800,
  },
)
*/
</script>

<template>
  <div v-if="$device.isMobile">
    <!-- Header bar -->
    <AppHeaderBarMobile :hide-on-scroll="true">
      <SearchInput
        v-model="filters.words"
        @submit="applyFilters"
      />
      <Toggle
        v-model:pressed="filtersDrawerOpen"
        class="Toggle"
      >
        <Filter
          :size="24"
          :stroke-width="2"
          class="filterIcon"
          :class="{ active: isFilterActive }"
        />
      </Toggle>
    </AppHeaderBarMobile>

    <!-- Filters drawer -->
    <aside>
      <ItemExploreFiltersDrawer />
    </aside>

    <!-- Item cards -->
    <main>
      <ItemCardsCollection
        :items="items"
      />
    </main>
  </div>
  <div v-else>
    <!-- Filters panel -->
    <aside>
      <ItemExploreFiltersPanel />
    </aside>
    <div>
      <header>
        <SearchInput
          v-model="searchInput"
          @submit="applyFilters()"
        />
      </header>

      <!-- Item cards -->
      <main>
        <ItemCardsCollection
          :items="items"
        />
      </main>
    </div>
    <aside />
  </div>
</template>

<style scoped lang="scss">
</style>
