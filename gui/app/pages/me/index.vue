<script setup lang="ts">
import {
  UserRound,
  Heart,
  Package,
  Gift,
  UserPen,
  LockKeyhole,
  Info,
  MessageCircleQuestion,
  Scale,
  AtSign,
} from 'lucide-vue-next'

// get main header bar height to offset content
const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

// auth session
const { loggedIn } = useAuth()
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <UserRound
        :size="32"
        :stroke-width="2"
        :absolute-stroke-width="true"
      />
      <h1>Mes activités & options</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main class="app-content ">
      <h2 v-if="loggedIn === true">
        Activités
      </h2>
      <SlabList v-if="loggedIn === true">
        <NuxtLink to="/me/liked">
          <MeSlab>
            Objets aimés
            <template #image>
              <Heart
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/borrowings">
          <MeSlab>
            Mes emprunts
            <template #image>
              <Package
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/loans">
          <MeSlab>
            Mes prêts
            <template #image>
              <Gift
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
      </SlabList>

      <h2>Options</h2>
      <SlabList>
        <NuxtLink to="/me/profile">
          <MeSlab v-if="loggedIn === true">
            Profile
            <template #image>
              <UserPen
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/account">
          <MeSlab>
            Compte
            <template #image>
              <LockKeyhole
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
      </SlabList>

      <h2>Info</h2>
      <SlabList>
        <NuxtLink to="/me/info">
          <MeSlab>
            A propos de BabyTroc
            <template #image>
              <Info
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/faq">
          <MeSlab>
            FAQ
            <template #image>
              <MessageCircleQuestion
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/politics">
          <MeSlab>
            Politiques
            <template #image>
              <Scale
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
        <NuxtLink to="/me/contact">
          <MeSlab>
            Contact
            <template #image>
              <AtSign
                :size="32"
                :stroke-width="2"
                :absolute-stroke-width="true"
              />
            </template>
          </MeSlab>
        </NuxtLink>
      </SlabList>
    </main>
  </div>
</template>

<style scoped lang="scss">
.app-content {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
