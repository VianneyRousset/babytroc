<script setup lang="ts">

import { ArrowLeft, Ellipsis, Heart } from 'lucide-vue-next';
import { computedAsync } from '@vueuse/core'

const { $api } = useNuxtApp();

const route = useRoute();

const userId = computed(() => Number(route.params["user_id"]));

const routeStack = useRouteStack();

const usersStore = useUsersStore();

const user = computedAsync(async () => await usersStore.get(userId.value));

const fallback = computed(() => "/" + route.fullPath.split("/").filter(e => e)[0]);

</script>

<template>
  <div>

    <AppHeaderBar class="header-bar">

      <div>
        <AppBack :fallback="fallback" />
        <h1 :title="user?.name ?? '...'">{{ user?.name ?? '...' }}</h1>
        <Ellipsis style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </div>

      <div>
        <Avatar :seed="user?.avatar_seed" />
        <div class="counter">
          <div>{{ user?.stars_count ?? '...' }}</div>
          <div>Étoiles</div>
        </div>
        <div class="counter">
          <div>{{ user?.likes_count ?? '...' }}</div>
          <div>Likes</div>
        </div>
        <div class="counter">
          <div>{{ user?.items.length ?? '...' }}</div>
          <div>Objects</div>
        </div>
      </div>

    </AppHeaderBar>

    <div class="main">

      <!-- list of items -->
    </div>
  </div>
</template>

<style scoped lang="scss">
.header-bar {

  @include flex-column;
  align-items: stretch;
  padding: 0;
  gap: 0;
  height: 170px;

  &>div:first-child {
    @include flex-row;

    gap: 16px;
    padding: 0 1rem;

    h1 {
      @include ellipsis-overflow;
      flex-grow: 1;
      font-size: 1.6rem;
      font-weight: 500;
    }

  }

  &>div:last-child {
    @include flex-row;
    flex-grow: 1;
    justify-content: space-between;
    padding: 0 2rem;

    .counter {
      @include flex-column;

      &>div:first-child {
        font-size: 2rem;
        font-weight: 400;
        font-family: "Plus Jakarta Sans", sans-serif;
      }

      &>div:last-child {
        font-family: 'Inter', sans-serif;
        color: $neutral-400;
      }

    }

    gap: 16px;
    height: 64px;

    a {
      @include flex-row;
    }

    svg {
      stroke: $neutral-700;
    }

    h1 {
      @include ellipsis-overflow;
      flex-grow: 1;

      font-weight: 500;
      font-size: 1.6rem;
    }

  }
}

.main {
  padding-top: 170px;
  padding-bottom: 64px;
  box-sizing: border-box;
}
</style>
