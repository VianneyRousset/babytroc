<script setup lang="ts">

import { Filter, ArrowLeft, RotateCcw } from 'lucide-vue-next';
import { vInfiniteScroll } from '@vueuse/components'
import type { ApiRequestQuery } from '#open-fetch'

type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>;

const itemsStore = useAllItemsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));
const { height: filtersHeaderHeight } = useElementSize(useTemplateRef("filters-header"));

const filtersDrawerOpen = ref(false);

const route = useRoute();
const router = useRouter();

const searchInput = ref(Array.isArray(route.query.q) ? route.query.q.join(" ") : "");
const stateAvailable = ref(route.query.av !== "n");
const stateUnavailable = ref(route.query.av === "n" || route.query.av === "a");

const targetedAge = ref(typeof route.query.mo === "string" ? parseMonthRange(route.query.mo) : [0, null]);
const regions = reactive([1, 2, 3]);


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
    query.av = stateAvailable.value ? "a" : "n";

  // update page query params
  router.push({ query: query });
}

// update store query parameters on route query change
watch(() => route.query, (routeQuery) => {
  const query: ItemQuery = {
    n: 16,
  }

  // q
  if (typeof routeQuery.q === "string") {
    query.q = [routeQuery.q];
  } else if (Array.isArray(routeQuery.q)) {
    query.q = routeQuery.q as string[];
  }

  // mo
  if (typeof routeQuery.mo === 'string')
    query.mo = routeQuery.mo;

  // av
  if (typeof routeQuery.av === 'string' && ["y", "n", "a"].includes(routeQuery.av))
    query.av = routeQuery.av as ("y" | "n" | "a");

  itemsStore.setQuery(query);
},
  { immediate: true }
);

function resetFilters() {
  stateAvailable.value = true;
  stateUnavailable.value = false;
  targetedAge.value = [0, null];
  regions.splice(0);
}

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <SearchInput v-model="searchInput" @submit="go()" />
      <Toggle v-model:pressed="filtersDrawerOpen" class="Toggle">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
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
        <RotateCcw @click="resetFilters()" style="cursor: pointer" :size="32" :strokeWidth="2"
          :absoluteStrokeWidth="true" />
      </AppHeaderBar>

      <!-- Filters main -->
      <div class="app-content filters">
        <div class="page">

          <h2>Disponibilité</h2>
          <div class="checkbox-group">
            <Checkbox v-model="stateAvailable">Disponible</Checkbox>
            <Checkbox v-model="stateUnavailable">Non-disponible</Checkbox>
          </div>

          <h2>Age</h2>
          <AgeRangeInput v-model="targetedAge" />

          <h2>Régions</h2>
          <RegionsMap style="width: 100%; height: auto;" :actives="regions" />

        </div>
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
</style>
