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
            <div class="user-profile-card">
              <UserAvatar
                :seed="user.avatar_seed"
                class="avatar"
              />
              <h1>{{ user.name }}</h1>
              <div class="stats">
                <div class="stat">
                  <span class="value">{{ user.stars_count }}</span>
                  <span class="label">Étoiles</span>
                </div>
                <div class="stat">
                  <span class="value">{{ user.likes_count }}</span>
                  <span class="label">Likes</span>
                </div>
                <div class="stat">
                  <span class="value">{{ user.items_count }}</span>
                  <span class="label">Objets</span>
                </div>
              </div>
            </div>
            <section>
              <h2>Objets appartenant à {{ user.name }}</h2>
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

  gap: $space-8;

  section {
    display: flex;
    flex-direction: column;
    gap: $space-3;

    h2 {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 1.25rem;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
  }

  .user-profile-card {
    @include flex-column;
    align-items: center;
    padding: $space-10 $space-6;
    gap: $space-4;

    .avatar {
      width: 96px;
      height: 96px;
    }

    h1 {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .stats {
      display: flex;
      gap: 0;
      margin-top: $space-2;

      .stat {
        @include flex-column;
        align-items: center;
        padding: 0 $space-8;
        gap: $space-1;

        &:not(:last-child) {
          border-right: 1px solid $divider;
        }

        .value {
          @include font-jakarta;
          font-size: 1.25rem;
          font-weight: 700;
          color: $text-primary;
        }

        .label {
          font-size: 0.75rem;
          color: $text-secondary;
        }
      }
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
