<script setup lang="ts">

import { Bookmark } from 'lucide-vue-next';
import { vInfiniteScroll } from '@vueuse/components'

const savedItemsStore = useSavedItemsStore();
const routeStack = useRouteStack();

</script>


<template>
  <div>

    <AppHeaderBar class="header-bar">
      <Bookmark :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <h1>Objets sauvegardés</h1>
    </AppHeaderBar>


    <div class="main">

      <!-- list of items -->
      <ItemCardsList v-if="savedItemsStore.items?.length" :items="savedItemsStore.items" target="saved-item-item_id" />

      <!-- loader -->
      <div v-else-if="savedItemsStore.status === 'pending'" class="loader">
        <div class="loader">
          <Loader />
        </div>
      </div>

      <!-- no items -->
      <div v-else-if="savedItemsStore.items?.length === 0" class="no-result">
        Aucun objets sauvegardés
      </div>

    </div>

  </div>
</template>

<style scoped lang="scss">
.header-bar {

  @include flex-row;
  gap: 16px;
  height: 64px;

  svg {
    stroke: $neutral-500;
  }

  h1 {
    @include ellipsis-overflow;
    flex-grow: 1;

    font-weight: 500;
    font-size: 1.6rem;
  }

}

.main {

  padding-top: 64px;
  padding-bottom: 64px;
  box-sizing: border-box;
  height: 100vh;
  overflow-y: scroll;

  .loader {

    @include flex-column;
    margin-top: 1em;
    margin-bottom: 1em;
  }

  .no-result {

    @include flex-column;
    margin-top: 2em;

    color: $neutral-300;
    font-size: 1rem;

  }
}
</style>
