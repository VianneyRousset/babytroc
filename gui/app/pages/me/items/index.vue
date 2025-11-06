<script setup lang="ts">
import { CirclePlus } from 'lucide-vue-next'

definePageMeta({
  layout: 'me',
})

// query items
const { items, error, isLoading, loadMore: loadMoreItems } = useMeItems()

// auth
useAuth({ fallbackRoute: '/me' })

const openItem = (itemId: number) => navigateTo(`/me/items/${itemId}`)
</script>

<template>
  <AppPage
    with-header
    :max-width="1000"
    infinite-scroll
    :infinite-scroll-distance="1800"
    @more="loadMoreItems"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>
        Mes objets
      </h1>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
        <template #buttons-right>
          <TextButton
            target="/me/items/new"
            aspect="outline"
            color="primary"
            :icon="CirclePlus"
          >
            Ajouter un objet
          </TextButton>
        </template>
        <h1>Mes objets</h1>
      </AppHeaderDesktop>
    </template>

    <!-- Item cards -->
    <main>
      <Panel>
        <ItemCardsCollection
          :items="items"
          :loading="isLoading"
          :error="error != null"
          @select="openItem"
        />
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
:deep(.Panel.desktop .content) {

  gap: 2em;

  .InfoBox {
    border-radius: 2em;

    .content {
      @include flex-row;
      gap: 4em;
      padding: 2em 4em;
    }

    font-size: clamp(0.6em, 1.5vw, 1em);

    .avatar-name {
      @include flex-column;
      flex: 2;
      gap: 1em;
      .UserAvatar {
        width: 60%;
      }
      h1 {
        margin: 0;
        text-align: center;
      }
    }

    .counters {
      @include flex-row;
      gap: 2em;
      justify-content: center;
      flex: 5;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
