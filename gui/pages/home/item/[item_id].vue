<script setup lang="ts">

import { Bookmark, BookmarkX, ShieldAlert } from 'lucide-vue-next';
import { computedAsync } from '@vueuse/core'

// get item ID from route
const route = useRoute();
const itemId = Number(route.params["item_id"]);

// get main header bar height to offset content
const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

// get item data
const { data: item, refresh: refreshItem } = await useApi('/v1/items/{item_id}', {
  path: {
    item_id: itemId,
  },
  key: `item/${itemId}`
});

const { name, isOwnedByUser, images, regions, regionsIds, ownerId, owner } = useItem(item);
const { isLikedByUser, likeStatus, toggleLike } = useItemLike(itemId, refreshItem);
const { isSavedByUser, saveStatus, toggleSave } = useItemSave(itemId);
const { isRequestedByUser, requestStatus, requestItem } = useItemLoanRequest(itemId);

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <AppBack />
      <h1 :title="name ?? undefined">{{ name }}</h1>

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

        <div v-if="item !== null" class="vbox">

          <!-- Gallery -->
          <Gallery :images="item?.images_names ?? []" />

          <!-- Availability and likes count -->
          <div class="hbox">
            <Availability :available="item?.available ?? false" :loading="true" />
            <Counter symbol="heart" size="normal" :count="item?.likes_count ?? 0" :active="isLikedByUser"
              :loading="likeStatus === 'pending'" @click="toggleLike()" />
          </div>

          <!-- Description -->
          <Fold title="Description">
            <p>{{ item.description }}</p>
          </Fold>

          <!-- Details (age and regions) -->
          <Fold title="Détails">
            <div class="minitable">
              <div class="label">Âge</div>
              <div>{{ formatTargetedAge(...item.targeted_age_months) }}</div>
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
          <UserCard :user="owner" target="home-user-user_id" />
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
