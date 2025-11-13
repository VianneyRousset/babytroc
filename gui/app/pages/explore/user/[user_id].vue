<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'

definePageMeta({
  layout: 'explore',
})

// get user ID from route
const route = useRoute()
const userId = Number.parseInt(route.params.user_id as string) // TODO avoid this hack

const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(userId)) navigateTo(`/${currentTab}`)

// get user data
const { user, isLoading } = useUser({ userId })

// query items
const { items, error: itemsError, isLoading: itemsIsLoading, loadMore: loadMoreItems } = useUserItems({ userId })

// auth
const { loggedIn } = useAuth()
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
      <div>
        <AppBack />
        <h1 :title="user?.name">
          {{ user?.name }}
        </h1>

        <!-- Dropdown menu -->
        <DropdownMenu v-if="loggedIn === true && user">
          <DropdownItem
            :icon="ShieldAlert"
            red
          >
            Signaler
          </DropdownItem>
        </DropdownMenu>
      </div>
      <div v-if="user">
        <UserAvatar :seed="user.avatar_seed" />
        <div class="counters">
          <VerticalCounter :model-value="user.stars_count">
            Étoiles
          </VerticalCounter>
          <VerticalCounter :model-value="user.likes_count">
            Likes
          </VerticalCounter>
          <VerticalCounter :model-value="user.items_count">
            Objets
          </VerticalCounter>
        </div>
      </div>
    </template>

    <!-- Mobile page -->
    <template #mobile>
      <main>
        <WithLoading :loading="!user && isLoading">
          <Panel v-if="user">
            <section>
              <ItemCardsCollection
                :items="items"
                :dense="false"
                :loading="itemsIsLoading"
                :error="itemsError != null"
                :target="itemId => `/explore/item/${itemId}`"
              />
            </section>
          </Panel>
        </WithLoading>
      </main>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
      <main>
        <WithLoading :loading="!user && isLoading">
          <Panel
            v-if="user"
            class="desktop"
          >
            <InfoBox>
              <div class="avatar-name">
                <UserAvatar :seed="user.avatar_seed" />
                <h1>{{ user.name }}</h1>
              </div>
              <div class="counters">
                <VerticalCounter
                  :model-value="user.stars_count"
                  size="large"
                >
                  Étoiles
                </VerticalCounter>
                <VerticalCounter
                  :model-value="user.likes_count"
                  size="large"
                >
                  Likes
                </VerticalCounter>
                <VerticalCounter
                  :model-value="user.items_count"
                  size="large"
                >
                  Objets
                </VerticalCounter>
              </div>
            </InfoBox>
            <section>
              <h2>Objects appartenants à {{ user.name }}</h2>
              <ItemCardsCollection
                :items="items"
                :dense="false"
                :loading="itemsIsLoading"
                :error="itemsError != null"
                :target="itemId => `/explore/item/${itemId}`"
              />
            </section>
          </Panel>
        </WithLoading>
      </main>
    </template>
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

:deep(.AppHeaderMobileBar) {
  flex-direction: column;
  align-items: stretch;
  height: auto;
  gap: 0;

  & > div {
    @include flex-row;
    align-items: center;
    justify-content: space-between;

    &:first-child {
      height: 64px;
      gap: 16px;
    }

    &:last-child {
      margin: 1em;
      gap: 2em;
      justify-content: center;
    }

    .counters {
      @include flex-row;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
