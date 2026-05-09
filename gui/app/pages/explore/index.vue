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

import { Filter, LayoutGrid, Grid3x3, ArrowLeft, Repeat, X } from 'lucide-vue-next'
import { AppPage } from '#components'
import { isEqual, cloneDeep } from 'lodash'

definePageMeta({
  layout: 'explore',
})

const device = useDevice()

// item filters
const { filters, isDefault: isFiltersDefault, reset: resetFilters, loadFiltersFromQueryParams, dumpFiltersAsQueryParams } = useItemFilters()

// synced store and route query params
const { queryParams } = useItemExploreQueryParams()

// update filters when route query params changes
watch(queryParams, newQueryParams => loadFiltersFromQueryParams(newQueryParams), { immediate: true })

// query items
const { items, error, isLoading, loadMore, end } = useItemExplore({ queryParams })

// filters are applied by updating the route query params
const applyFilters = () => (queryParams.value = dumpFiltersAsQueryParams())

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

// active filter chips
const { categories } = useCategoriesList()
const { regions } = useRegionsList()

type FilterChip = { label: string, remove: () => void }

const activeFilterChips = computed<FilterChip[]>(() => {
  const chips: FilterChip[] = []
  const f = unref(filters)

  if (!f.available && f.unavailable) {
    chips.push({ label: 'Non-disponible', remove: () => { f.available = true; f.unavailable = false } })
  } else if (f.available && f.unavailable) {
    chips.push({ label: 'Tous', remove: () => { f.available = true; f.unavailable = false } })
  }

  for (const slug of f.categories) {
    const cat = unref(categories)?.find(c => c.slug === slug)
    if (cat) {
      chips.push({ label: cat.name, remove: () => f.categories.delete(slug) })
    }
  }

  if (f.targetedAge[0] !== 0 || f.targetedAge[1] !== null) {
    const from = f.targetedAge[0]
    const to = f.targetedAge[1]
    const label = to == null ? `Dès ${from} mois` : `${from}–${to} mois`
    chips.push({ label, remove: () => { f.targetedAge = [0, null] } })
  }

  for (const regionId of f.regions) {
    const region = unref(regions)?.find(r => r.id === regionId)
    if (region) {
      chips.push({ label: region.name, remove: () => f.regions.delete(regionId) })
    }
  }

  return chips
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
          :icon="Filter"
          aria-label="Filtres"
        />
        <FloatingToggle
          v-model="dense"
          :aria-label="dense ? 'Affichage normal' : 'Affichage compact'"
        >
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
      <ConditionalDrawerOverlay
        v-model="filtersDrawerOpen"
        position="right"
        :drawer="drawerMode"
      >
        <Panel class="filters-panel">
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
              aria-label="Fermer les filtres"
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
              aria-label="Réinitialiser les filtres"
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
              aria-label="Réinitialiser les filtres"
              @click="resetFilters"
            >
              <Repeat
                :size="24"
                :stroke-width="2"
              />
            </IconButton>
          </template>
        </Panel>
      </ConditionalDrawerOverlay>
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
            aria-label="Filtres"
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
        <!-- Active filter chips -->
        <div
          v-if="activeFilterChips.length > 0"
          class="filter-chips"
        >
          <button
            v-for="chip in activeFilterChips"
            :key="chip.label"
            class="chip"
            @click="chip.remove(); applyFilters()"
          >
            {{ chip.label }}
            <X
              :size="14"
              :stroke-width="2"
              aria-hidden="true"
            />
          </button>
        </div>

        <ItemCardsCollection
          :items="items"
          :dense="dense"
          :loading="isLoading"
          :error="error != null"
          :target="itemId => `/explore/item/${itemId}`"
        />

        <!-- End of results -->
        <div
          v-if="end && items && items.length > 0 && !isLoading"
          class="end-message"
        >
          Plus d'objets à afficher
        </div>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.AppHeaderDesktop {
  font-size: clamp(0.8em, 1.5vw, 1em);
  h1 {
    text-align: center;
    color: $text-primary;
  }
  .SearchInput {
    width: 80%;
  }
}

.ToggleIcon.filter {
  margin-right: $space-16;
  color: $text-tertiary;
}

.floating-buttons {
  @include flex-column;
  gap: $space-2;
  position: absolute;
  right: $space-2;
  top: calc(var(--app-header-bar-height) + #{$space-2});
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: $space-2;
  padding: 0 $space-2;

  .chip {
    @include reset-button;
    display: flex;
    align-items: center;
    gap: $space-1;
    padding: $space-1 $space-3;
    background: $neutral-100;
    color: $text-secondary;
    border-radius: $radius-pill;
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 150ms ease-out;

    &:hover {
      background: $neutral-200;
      color: $text-primary;
    }

    &:focus-visible {
      outline: 2px solid $primary-500;
      outline-offset: 1px;
    }
  }
}

.filters-panel {
  align-items: stretch;
}

.end-message {
  text-align: center;
  color: $text-tertiary;
  font-size: 0.8125rem;
  padding: $space-8 0;
}
</style>
