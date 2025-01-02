<script setup lang="ts">

import { Search, Filter } from 'lucide-vue-next';

const route = useRoute();

// const { data } = await useFetch('localhost:8080/v1/item1');

// console.log(data);

</script>


<template>
  <div class="header-bar">

    <div class="search">
      <Search :size="24" :strokeWidth="1" :absoluteStrokeWidth="true" />
      <input placeholder=" Search" type="search" class="input">
    </div>

    <NuxtLink to="/home/filter">
      <Filter :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
    </NuxtLink>

  </div>


  <ItemList items="Put items here" />

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
