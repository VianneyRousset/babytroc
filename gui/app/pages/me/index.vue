<script setup lang="ts">
import {
  UserRound,
  Heart,
  Package,
  Gift,
  UserPen,
  LockKeyhole,
  LockKeyholeOpen,
  Info,
  MessageCircleQuestion,
  Scale,
  AtSign,
} from 'lucide-vue-next'

// auth session
const { loggedIn } = useAuth()
</script>

<template>
  <AppPage>
    <!-- Header bar -->
    <template #mobile-header-bar>
      <UserRound
        :size="32"
        :stroke-width="2"
      />
      <h1>Mes activités & options</h1>
    </template>

    <!-- Main content -->
    <Panel>
      <section>
        <h2 v-if="loggedIn === true">
          Activités
        </h2>
        <SlabList v-if="loggedIn === true">
          <NuxtLink to="/me/borrowings">
            <MeSlab>
              Mes emprunts
              <template #image>
                <Package
                  :size="32"
                  :stroke-width="2"
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
                />
              </template>
            </MeSlab>
          </NuxtLink>
        </SlabList>
      </section>
      <section>
        <h2>Options</h2>
        <SlabList>
          <NuxtLink to="/me/profile">
            <MeSlab v-if="loggedIn === true">
              Profile
              <template #image>
                <UserPen
                  :size="32"
                  :stroke-width="2"
                />
              </template>
            </MeSlab>
          </NuxtLink>
          <NuxtLink to="/me/account">
            <MeSlab>
              Compte
              <template #image>
                <LockKeyhole
                  v-if="loggedIn === true"
                  :size="32"
                  :stroke-width="2"
                />
                <LockKeyholeOpen
                  v-else
                  :size="32"
                  :stroke-width="2"
                />
              </template>
            </MeSlab>
          </NuxtLink>
        </SlabList>
      </section>
      <section>
        <h2>Info</h2>
        <SlabList>
          <NuxtLink to="/me/about">
            <MeSlab>
              A propos de BabyTroc
              <template #image>
                <Info
                  :size="32"
                  :stroke-width="2"
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
                />
              </template>
            </MeSlab>
          </NuxtLink>
        </SlabList>
      </section>
    </Panel>
  </AppPage>
</template>
