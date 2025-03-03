<script setup lang="ts">

import { Filter, ArrowLeft, Repeat } from 'lucide-vue-next';

import { ItemQueryAvailability } from '#build/types/open-fetch/schemas/api';

const itemsStore = useAllItemsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));
const { height: filtersHeaderHeight } = useElementSize(useTemplateRef("filters-header"));

const filtersDrawerOpen = ref(false);

const route = useRoute();
const router = useRouter();

const searchInput = ref(getQueryParamAsArray(route.query, "q").join(" "));
const stateAvailable = ref(route.query.av !== ItemQueryAvailability.no);
const stateUnavailable = ref(route.query.av === ItemQueryAvailability.no || route.query.av === ItemQueryAvailability.all);

const targetedAge = ref(typeof route.query.mo === "string" ? parseMonthRange(route.query.mo) : [0, null]);
const regions = reactive(new Set(getQueryParamAsArray(route.query, "reg").map(Number)));

const isFilterActive = computed(() => {

  if (typeof route.query.mo === 'string')
    return true;

  if (typeof route.query.av === 'string' && Object.values(ItemQueryAvailability).includes(route.query.av as ItemQueryAvailability))
    return true;

  if (route.query.reg)
    return true;

  return false;
});

const areFilterInputsChanged = computed(() => {

  if (!stateAvailable.value)
    return true;

  if (stateUnavailable.value)
    return true;

  if (targetedAge.value[0] !== 0 || targetedAge.value[1] !== null)
    return true;

  if (regions.size > 0)
    return true;

  return false;
});

function go() {
  const query: ItemQuery = {}

  // text search
  const q = searchInput.value.split(" ").filter((word => word.length > 0));
  if (q.length > 0)
    query.q = q;

  // targeted age
  if ((targetedAge.value[0] ?? 0) > 0 || targetedAge.value[1] !== null)
    query.mo = formatMonthRange(targetedAge.value);

  // availability
  if (stateUnavailable.value)
    query.av = (stateAvailable.value ? ItemQueryAvailability.all : ItemQueryAvailability.no) as ItemQueryAvailability;

  // regions
  if (regions.size > 0)
    query.reg = Array.from(regions);

  // update page query params
  router.push({ query: query });
}

// update store query parameters on route query change
watch(() => route.query, (routeQuery) => {
  const query: ItemQuery = {
    n: 16,
  }

  // q
  if (routeQuery.q)
    query.q = getQueryParamAsArray(routeQuery, "q");

  // mo
  if (typeof routeQuery.mo === 'string')
    query.mo = routeQuery.mo;

  // av
  if (typeof routeQuery.av === 'string' && Object.values(ItemQueryAvailability).includes(routeQuery.av as ItemQueryAvailability))
    query.av = routeQuery.av as ItemQueryAvailability;

  // reg
  if (routeQuery.reg)
    query.reg = getQueryParamAsArray(routeQuery, "reg").map(Number);

  itemsStore.setQuery(query);
},
  { immediate: true }
);

function resetFilterInputs() {
  stateAvailable.value = true;
  stateUnavailable.value = false;
  targetedAge.value = [0, null];
  regions.clear();
}

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <SearchInput v-model="searchInput" @submit="go()" />
      <Toggle v-model:pressed="filtersDrawerOpen" class="Toggle">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" class="filterIcon"
          :class="{ active: isFilterActive }" />
      </Toggle>
    </AppHeaderBar>

    <!-- Filters drawer -->
    <Drawer v-model="filtersDrawerOpen">

      <!-- Filters header bar -->
      <AppHeaderBar ref="filters-header">
        <Toggle v-model:pressed="filtersDrawerOpen" class="Toggle" @click="go()">
          <ArrowLeft :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
        </Toggle>
        <h1>Filtres</h1>
        <IconButton :disabled="!areFilterInputsChanged" @click="resetFilterInputs()">
          <Repeat :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
        </IconButton>
      </AppHeaderBar>

      <!-- Filters main -->
      <div class="app-content filters page">

        <h2>Disponibilité</h2>
        <div class="checkbox-group">
          <Checkbox v-model="stateAvailable">Disponible</Checkbox>
          <Checkbox v-model="stateUnavailable">Non-disponible</Checkbox>
        </div>

        <h2>Age</h2>
        <AgeRangeInput v-model="targetedAge" />

        <h2>Régions</h2>
        <RegionsMap v-model="regions" />
        <RegionsCheckboxes v-model="regions" />

      </div>
    </Drawer>

    <!-- Main content -->
    <main>
      <ItemCardsList :src="itemsStore" target="home-item-item_id" ref="main" class="app-content page" />
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.filters.app-content {
  --header-height: v-bind(filtersHeaderHeight + "px");
}

.filterIcon.active {
  stroke: $primary-400;
  filter: drop-shadow(0px 0px 2px $primary-200);

}
</style>
