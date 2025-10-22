<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'

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

const openItem = (itemId: number) => navigateTo(`/explore/item/${itemId}`)
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
      <h1 :title="user?.name">
        {{ user?.name }}
      </h1>

      <!-- Dropdown menu -->
      <DropdownMenu v-if="loggedIn === true">
        <DropdownMenuItem class="red">
          <ShieldAlert
            style="cursor: pointer;"
            :size="32"
            :stroke-width="2"
          />
          <div>Signaler</div>
        </DropdownMenuItem>
      </DropdownMenu>
    </template>

    <!-- Mobile page -->
    <template #mobile>
      <main>
        <WithLoading :loading="!user && isLoading">
          <Panel v-if="user">
            <!-- Item collection -->
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
                  orientation="vertical"
                  :model-value="user.stars_count"
                >
                  Étoiles
                </VerticalCounter>
                <VerticalCounter
                  orientation="vertical"
                  :model-value="user.likes_count"
                >
                  Likes
                </VerticalCounter>
                <VerticalCounter
                  orientation="vertical"
                  :model-value="user.items_count"
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
                @select="openItem"
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

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
