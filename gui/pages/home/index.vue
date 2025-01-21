<script setup lang="ts">

import { Search, Filter, X } from 'lucide-vue-next';
import { vInfiniteScroll } from '@vueuse/components'

const itemsStore = useAllItemsStore();
const routeStack = useRouteStack();

routeStack.reset();

function canLoadMore() {
  return itemsStore.canFetchMore;
}

function onLoadMore() {

  if (itemsStore.firstFetchStatus === 'pending' || itemsStore.extraFetchStatus === 'pending')
    return;

  itemsStore.fetchMore();
}

function onInputEnter(event: Event) {

  if (event.target instanceof HTMLElement)
    event.target.blur();

  itemsStore.refresh();
}

function onInputEscape(event: Event) {

  if (event.target instanceof HTMLElement)
    event.target.blur();

  clearSearch();
}

function clearSearch() {
  itemsStore.filters.searchText = "";
  itemsStore.refresh()
}

</script>


<template>
  <div>

    <AppHeaderBar class="header-bar">

      <div class="search">
        <Search :size="20" :strokeWidth="1" :absoluteStrokeWidth="true" />
        <input v-model="itemsStore.filters.searchText" placeholder="Search" type="search" class="input" tabindex="1"
          autofocus @keyup.enter="onInputEnter" @keyup.escape="onInputEscape">
        <X v-if="itemsStore.filters.searchText !== ''" @click="clearSearch" :size="20" :strokeWidth="1"
          :absoluteStrokeWidth="true" />
      </div>

      <NuxtLink to="/home/filter">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </NuxtLink>

    </AppHeaderBar>


    <div class="main" v-infinite-scroll="[onLoadMore, { distance: 600, canLoadMore: () => itemsStore.canFetchMore }]">

      <!-- first items fetch error -->
      <div v-if="itemsStore.firstFetchStatus === 'error'">{{ itemsStore.firstFetchError }}</div>

      <!-- list of items -->
      <ItemCardsList :items="itemsStore.items" target="home-item-item_id" />

      <!-- extra items fetch error -->
      <div v-if="itemsStore.extraFetchStatus === 'error'">{{ itemsStore.extraFetchError }}</div>

      <!-- loader -->
      <div v-else-if="itemsStore.firstFetchStatus === 'pending' || itemsStore.extraFetchStatus === 'pending'"
        class="loader">
        <div class="loader">
          <Loader />
        </div>
      </div>

      <!-- no items -->
      <div v-else-if="itemsStore.items.length === 0" class="no-result">
        Aucun résultat
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

  input {
    font-family: inherit;
  }

  .search {

    flex-grow: 1;

    display: flex;
    line-height: 28px;
    align-items: center;
    position: relative;

    svg {
      position: absolute;
      stroke: $neutral-400;

      &:first-child {
        left: 0.7rem;
      }

      &:last-child {
        right: 0.7rem;
        cursor: pointer;
      }
    }

    input {
      width: 100%;
      height: 42px;
      border: 2px solid $neutral-100;
      border-radius: 8px;
      background-color: #ffffff;
      line-height: 28px;
      padding: 0 2.5rem;
      outline: none;
      transition: .3s ease;

      &::placeholder {
        color: #9e9ea7;
      }

      &:focus,
      &:hover {
        outline: none;
        border-color: $primary-200;
        box-shadow: 0 0 0 2px $primary-50;
      }

    }
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
