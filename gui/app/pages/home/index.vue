<script setup lang="ts">
import { Filter, ArrowLeft, Repeat } from "lucide-vue-next";

import { ItemQueryAvailability } from "#build/types/open-fetch/schemas/api";

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(
	useTemplateRef("main-header"),
);
const { height: filtersHeaderHeight } = useElementSize(
	useTemplateRef("filters-header"),
);

const filtersDrawerOpen = ref(false);

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

// query items
const {
	query,
	data: itemsPages,
	status: itemsStatus,
	asyncStatus: itemsAsyncStatus,
	loadMore,
} = useItemsListQuery();

const {
	searchInput,
	stateAvailable,
	stateUnavailable,
	targetedAge,
	regions,
	isFilterActive,
	areFilterInputsChanged,
	filter,
} = useItemFilters();

// update store query parameters on route query change
watch(
	() => route.query,
	(routeQuery) => {
		query.value = {
			q: routeQuery.q ? getQueryParamAsArray(routeQuery, "q") : undefined,
			mo: typeof routeQuery.mo === "string" ? routeQuery.mo : undefined,
			av:
				typeof routeQuery.av === "string" &&
				Object.values(ItemQueryAvailability).includes(
					routeQuery.av as ItemQueryAvailability,
				)
					? (routeQuery.av as ItemQueryAvailability)
					: undefined,
			reg: routeQuery.reg
				? getQueryParamAsArray(routeQuery, "reg").map(Number.parseInt)
				: undefined,
		};
	},
	{
		immediate: true,
	},
);

function resetFilterInputs() {
	stateAvailable.value = true;
	stateUnavailable.value = false;
	targetedAge.value = [0, null];
	regions.clear();
}

// const { status: likedItemsStatus, data: likedItems } = useLikedItemsQuery();
// const { status: savedItemsStatus, data: savedItems } = useSavedItemsQuery();

const likedItems = Array<ItemPreview>();
const savedItems = Array<ItemPreview>();

function openItem(itemId: number) {
	routeStack.amend(
		router.resolve({ ...route, hash: `#item-${itemId}` }).fullPath,
	);
	return navigateTo(`/home/item/${itemId}`);
}

const { reset } = useInfiniteScroll(
	main,
	async () => {
		await loadMore();
	},
	{
		canLoadMore: () => !unref(itemsPages).end,
		distance: 1800,
	},
);
</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <SearchInput v-model="searchInput" @submit="filter()" />
      <Toggle v-model:pressed="filtersDrawerOpen" class="Toggle">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" class="filterIcon"
          :class="{ active: isFilterActive }" />
      </Toggle>
    </AppHeaderBar>

    <!-- Filters drawer -->
    <Drawer v-model="filtersDrawerOpen">

      <!-- Filters header bar -->
      <AppHeaderBar ref="filters-header">
        <Toggle v-model:pressed="filtersDrawerOpen" class="Toggle" @click="filter()">
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
      <List v-if="likedItems && savedItems" ref="main" class="app-content page">
        <ItemCard v-for="item in itemsPages.data ?? []" @click="openItem(item.id)" :key="`item-${item.id}`"
          :id="`item-${item.id}`" :item="item" :likedItems="likedItems" :savedItems="savedItems" />
        <ListError v-if="itemsStatus === 'error'">Une erreur est survenue.</ListError>
        <ListLoader v-if="itemsAsyncStatus === 'loading'" />
        <ListEmpty v-else-if="itemsPages.data.length === 0">Aucun résultat</ListEmpty>
      </List>
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
  overflow-y: scroll;
}

.filters.app-content {
  --header-height: v-bind(filtersHeaderHeight + "px");
}

.filterIcon.active {
  stroke: $primary-400;
  filter: drop-shadow(0px 0px 2px $primary-200);

}
</style>
