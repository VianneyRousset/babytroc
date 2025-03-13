<script setup lang="ts">

import { Bookmark, BookmarkX, ShieldAlert } from 'lucide-vue-next';

// get item ID from route
const route = useRoute();
const itemId = Number.parseInt(route.params["item_id"] as string); // TODO avoid this hack

// get main header bar height to offset content
const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

// current tab
const { currentTab } = useTab();

// get item data
const { data: cachedItem } = useNuxtData(`item-${itemId}`);
const { data: item, refresh: refreshItem, status } = await useLazyApi('/v1/items/{item_id}', {
  path: {
    item_id: itemId,
  },
  key: `item-${itemId}`,
  server: false,
  cache: "default",
  default: () => unref(cachedItem),
});

// true if loader should be shown
const loader = computed(() => item.value === null && status.value !== "success");

const {
  name,
  isOwnedByUser,
  images,
  description,
  formatedTargetedAgeMonths,
  available,
  likesCount,
  regions,
  regionsIds,
  ownerId,
  owner,
} = useItem(item);
const { isLikedByUser, likeStatus, toggleLike } = useItemLike(itemId, refreshItem);
const { isSavedByUser, saveStatus, toggleSave } = useItemSave(itemId);
const { isRequestedByUser, requestStatus, requestItem } = useItemLoanRequest(itemId);

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <AppBack />
      <h1 :title="name ?? undefined">{{ name ?? "..." }}</h1>

      <!-- Dropdown menu -->
      <DropdownMenu>

        <DropdownMenuItem v-if="!isSavedByUser" class="DropdownMenuItem" @click="toggleSave()">
          <Bookmark style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
          <div>Enregistrer</div>
        </DropdownMenuItem>

        <DropdownMenuItem v-else class="DropdownMenuItem" @click="toggleSave()">
          <BookmarkX style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
          <div>Oublier</div>
        </DropdownMenuItem>

        <DropdownMenuItem class="DropdownMenuItem red">
          <ShieldAlert style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
          <div>Signaler</div>
        </DropdownMenuItem>

      </DropdownMenu>

    </AppHeaderBar>

    <!-- Main content -->
    <main ref="main">
      <div class="app-content page">

        <div class="vbox">

          <!-- Gallery -->
          <Gallery :images="images ?? []" :loading="loader" />

          <!-- Availability and likes count -->
          <div class="hbox">
            <Availability :available="available" :loading="true" />
            <Counter symbol="heart" size="normal" :count="likesCount" :active="isLikedByUser"
              :loading="likeStatus === 'pending'" @click="toggleLike()" />
          </div>

          <!-- Description -->
          <Fold>
            <template v-slot:title>Description</template>
            {{ description }}
          </Fold>

          <!-- Details (age and regions) -->
          <Fold>
            <template v-slot:title>Détails</template>
            <div class="minitable">
              <div class="label">Âge</div>
              <div>{{ formatedTargetedAgeMonths ?? "..." }}</div>
              <div class="label">Régions</div>
              <ul>
                <li v-for="region in regions">{{ region.name }}</li>
              </ul>
            </div>
            <RegionsMap :modelValue="regionsIds" />
          </Fold>

        </div>

        <!-- Owner -->
        <ClientOnly>
          <UserCard :user="owner" :target="`${currentTab}-user-user_id`" />
        </ClientOnly>

        <!-- Request button -->
        <BigButton type="bezel" v-if="!isOwnedByUser" :loading="requestStatus === 'pending'"
          :disabled="isRequestedByUser" @click="requestItem">
          {{ isRequestedByUser ? "Demande envoyée" : "Demander" }}
        </BigButton>

      </div>

    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
