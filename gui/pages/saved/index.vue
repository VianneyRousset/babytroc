<script setup lang="ts">

import { Bookmark } from 'lucide-vue-next';

const savedItemsStore = useSavedItemsStore();

const main = useTemplateRef<HTMLElement>("main");
const { height: mainHeaderHeight } = useElementSize(useTemplateRef("main-header"));

const { status: likedItemsStatus, data: likedItems } = useLikedItemsQuery();
const { status: savedItemsStatus, data: savedItems } = useSavedItemsQuery();

const route = useRoute();
const router = useRouter();
const routeStack = useRouteStack();

function openItem(itemId: number) {
  routeStack.amend(router.resolve({ ...route, hash: `#item${itemId}` }).fullPath);
  return navigateTo(`/home/item/${itemId}`);
}

</script>

<template>
  <div>

    <!-- Header bar -->
    <AppHeaderBar v-if="main !== null" ref="main-header" :scroll="main ?? false" :scrollOffset="32">
      <Bookmark :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <h1>Objets sauvegardés</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <List v-if="likedItems && savedItems" ref="main" class="app-content page">
        <ItemCard v-for="item in savedItems ?? []" @click="openItem(item.id)" :key="`item-${item.id}`"
          :id="`item-${item.id}`" :item="item" :likedItems="likedItems!" :savedItems="savedItems!" />
        <ListError v-if="savedItemsStatus === 'error'">Une erreur est survenue.</ListError>
        <ListLoader v-if="savedItemsStatus === 'pending'" />
        <ListEmpty v-else-if="savedItems.length === 0">Aucun objet sauvegardé</ListEmpty>
      </List>
    </main>

  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
