<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';
import { Search, Filter } from 'lucide-vue-next';

type ItemList = ApiResponse<'list_items_v1_items_get'>;
type Item = ItemList[number];

const searchText = ref("");
const wordsQuery = computed(() => {
  return searchText.value.split(" ").filter((word => word.length > 0));
});

const { data: items, pending, error, refresh } = await useApi('/v1/items', {
  query: {
    n: 32,
    q: wordsQuery,
  },
  key: "/items", // provided to avoid missmatch with ssr (bug with openfetch?)
});

</script>


<template>
  <div class="main">

    <AppHeaderBar class="header-bar">

      <div class="search">
        <Search :size="20" :strokeWidth="1" :absoluteStrokeWidth="true" />
        <input v-model="searchText" placeholder="Search" type="search" class="input" tabindex="1">
      </div>

      <NuxtLink to="/home/filter">
        <Filter :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </NuxtLink>

    </AppHeaderBar>


    <div v-if="error">Error: {{ error }}</div>
    <div v-else-if="pending">
      <div class="loader">
        <Loader />
      </div>
    </div>
    <div v-else-if="items && items.length > 0">
      <ItemCardsList :items="items" />
    </div>
    <div v-else="items" class="no-result">
      Aucun résultat
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
      left: 0.7rem;
      stroke: $neutral-400;
    }

    input {
      width: 100%;
      height: 42px;
      border: 2px solid $neutral-100;
      border-radius: 8px;
      background-color: #ffffff;
      line-height: 28px;
      padding: 0 1rem;
      padding-left: 2.5rem;
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

  .loader {

    @include flex-column;
    margin-top: 1em;
  }

  .no-result {

    @include flex-column;
    margin-top: 2em;

    color: $neutral-300;
    font-size: 1rem;

  }
}
</style>
