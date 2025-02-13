<script setup lang="ts">

import { Filter, ArrowLeft, X } from 'lucide-vue-next';
import { vInfiniteScroll } from '@vueuse/components'

const itemsStore = useAllItemsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));
const { height: filtersHeaderHeight } = useElementSize(useTemplateRef("filters-header"));

const filtersDrawerOpen = ref(false);

const searchInput = ref("");

function go() {
  console.log("go");
  itemsStore.query.q = searchInput.value.split(" ").filter((word => word.length > 0));
  itemsStore.reset();
}

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <SearchInput v-model="searchInput" @submit="go()" />
      <Toggle v-model="filtersDrawerOpen">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </Toggle>
    </AppHeaderBar>

    <!-- Filters drawer -->
    <Drawer v-model="filtersDrawerOpen">

      <!-- Filters header bar -->
      <AppHeaderBar ref="filters-header">
        <Toggle v-model="filtersDrawerOpen">
          <ArrowLeft :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
        </Toggle>
        <h1>Filtres</h1>
        <X :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </AppHeaderBar>

      <!-- Filters main -->
      <div class="app-content filters">
        <div class="page">
          <h2>Age</h2>
          <input type="range" min="1" max="100" value="50" class="slider" id="myRange">

          <h2>Disponibilité</h2>
          <input type="checkbox" id="vehicle1" name="vehicle1" value="Bike">
          <label for="vehicle1"> I have a bike</label><br>
          <input type="checkbox" id="vehicle1" name="vehicle1" value="Bike">
          <label for="vehicle1"> I have a bike</label><br>

          <h2>Régions</h2>
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
