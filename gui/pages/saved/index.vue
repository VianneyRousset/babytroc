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

    </div>

  </div>
</template>

<style scoped lang="scss">
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
