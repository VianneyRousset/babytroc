<script setup lang="ts">
import { Bookmark, LockKeyholeOpen } from 'lucide-vue-next'

const main = useTemplateRef<HTMLElement>('main')
const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const { loggedIn, loggedInStatus, loginRoute } = useAuth()
const { data: likedItems } = useLikedItemsQuery()
const { status: savedItemsStatus, data: savedItems } = useSavedItemsQuery()

const route = useRoute()
const router = useRouter()
const routeStack = useRouteStack()

function openItem(itemId: number) {
  routeStack.amend(
    router.resolve({ ...route, hash: `#item${itemId}` }).fullPath,
  )
  return navigateTo(`/home/item/${itemId}`)
}
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar
      ref="main-header"
      :scroll="main ?? false"
      :scroll-offset="32"
    >
      <Bookmark
        :size="32"
        :stroke-width="2"
        :absolute-stroke-width="true"
      />
      <h1>Objets sauvegardés</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <!-- Loader when not knowing if logged in -->
      <div
        v-if="loggedInStatus === 'pending'"
        class="app-content flex-column-center"
      >
        <LoadingAnimation />
      </div>

      <!-- Not logged in prompt -->
      <div
        v-else-if="loggedIn === false"
        class="app-content flex-column-center"
      >
        <div class="lock">
          <LockKeyholeOpen
            :size="48"
            :stroke-width="3"
            :absolute-stroke-width="true"
          />
          <div>Vous n'êtes pas connecté</div>
          <TextButton
            aspect="outline"
            @click="navigateTo(loginRoute)"
          >
            Se connecter
          </TextButton>
        </div>
      </div>

      <!-- Logged in: show the list of saved items -->
      <div
        v-else-if="loggedIn === true"
        ref="main"
      >
        <List
          v-if="savedItems"
          class="main app-content page"
        >
          <ItemCard
            v-for="item in savedItems"
            :id="`item${item.id}`"
            :key="`item${item.id}`"
            :item="item"
            :liked-items="likedItems ?? []"
            :saved-items="savedItems!"
            @click="openItem(item.id)"
          />
          <ListError v-if="savedItemsStatus === 'error'">
            Une erreur est survenue.
          </ListError>
          <ListLoader v-if="savedItemsStatus === 'pending'" />
          <ListEmpty v-else-if="savedItems.length === 0">
            Aucun objet sauvegardé
          </ListEmpty>
        </List>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.lock {
  @include flex-column-center;
  gap: 1rem;
  color: $neutral-800;
}
</style>
