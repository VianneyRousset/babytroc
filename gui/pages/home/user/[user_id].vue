<script setup lang="ts">

import { Bookmark, BookmarkX, ShieldAlert } from 'lucide-vue-next';
import { computedAsync } from '@vueuse/core'

const itemsStore = useAllItemsStore();

// get user ID from route
const route = useRoute();
const userId = Number(route.params["user_id"]);

// get main header bar height to offset content
const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

// current tab
const { currentTab } = useTab();

// get user data from store
const usersStore = useUsersStore();
const pendingUser = ref(false);
const user = computedAsync(
  async () => (await usersStore.get(userId)).value,
  null,
  {
    evaluating: pendingUser,
  },
);

const { name, avatarSeed, items, itemsSource, likesCount, starsCount, itemsCount } = useUser(user);

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">


      <div>
        <AppBack />
        <h1 :title="name ?? undefined">{{ name ?? "..." }}</h1>

        <!-- Dropdown menu -->
        <DropdownMenu>

          <DropdownMenuItem class="DropdownMenuItem red">
            <ShieldAlert style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
            <div>Signaler</div>
          </DropdownMenuItem>

        </DropdownMenu>

      </div>

      <div>
        <Avatar :seed="avatarSeed" />
        <div class="counter">
          <div>{{ starsCount ?? '...' }}</div>
          <div>Étoiles</div>
        </div>
        <div class="counter">
          <div>{{ likesCount ?? '...' }}</div>
          <div>Likes</div>
        </div>
        <div class="counter">
          <div>{{ itemsCount ?? '...' }}</div>
          <div>Objects</div>
        </div>
      </div>

    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <ItemCardsList ref="main" :src="itemsSource" :target="`${currentTab}-item-item_id`" class="app-content page" />
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

:deep(.AppHeaderBar) {

  @include flex-column;
  align-items: stretch;
  padding: 0;
  gap: 0;
  height: 170px;

  &>div:first-child {
    @include flex-row;

    height: 64px;
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
