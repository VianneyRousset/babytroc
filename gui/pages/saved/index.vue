<script setup lang="ts">

import { Bookmark } from 'lucide-vue-next';

const savedItemsStore = useSavedItemsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

</script>


<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <Bookmark :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <h1>Objets sauvegardés</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <ItemCardsList :src="savedItemsStore" target="saved-item-item_id" ref="main" class="app-content page" />
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
