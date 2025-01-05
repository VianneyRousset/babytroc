<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';
import { Search, Filter } from 'lucide-vue-next';

type ItemList = ApiResponse<'list_items_v1_items_get'>;
type Item = ItemList[number];

//const { data: items, pending, error } = await useFetch<ItemList>('/api/v1/items', {
//  query: { n: 32 },
//});
//

const { data: items, pending, error } = await useApi('/v1/items', {
  query: { n: 32 },
  key: "/items", // provided to avoid missmatch with ssr (bug with openfetch?)
});

</script>


<template>
  <div>

    <div class="header-bar">

      <div class="search">
        <Search :size="24" :strokeWidth="1" :absoluteStrokeWidth="true" />
        <input placeholder="Search" type="search" class="input" tabindex="1">
      </div>

      <NuxtLink to="/home/filter">
        <Filter :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </NuxtLink>

    </div>


    <div v-if="error">Error: {{ error }}</div>
    <div v-else-if="pending">Loading...</div>
    <div v-else>
      <ItemCardsList :items="items" />
    </div>

  </div>
</template>

<style scoped lang="scss">
.header-bar {

  @include flex-row;
  gap: 16px;

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
</style>
