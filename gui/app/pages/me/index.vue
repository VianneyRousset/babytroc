<script setup lang="ts">
import type { LucideIcon } from 'lucide-vue-next'
import {
  UserRound,
  Timer,
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

definePageMeta({
  layout: 'me',
})

// auth session
const { loggedIn } = useAuth()

type SlabData = {
  icon: LucideIcon
  target: string
  text: string
}

type SectionData = {
  title: string
  logged?: boolean
  slabs: Array<SlabData>
}

const sections = computed<Array<SectionData>>(() => [
  {
    title: 'Mes activités & options',
    logged: true,
    slabs: [
      { icon: Package, target: '/me/items', text: 'Mes objets' },
      { icon: Gift, target: '/me/loans', text: 'Mes prêts' },
      { icon: Timer, target: '/me/borrowings', text: 'Mes emprunts' },
    ],
  },
  {
    title: 'Options',
    logged: true,
    slabs: [
      { icon: UserPen, target: '/me/profile', text: 'Profile' },
      { icon: LockKeyhole, target: '/me/account', text: 'Compte' },
    ],
  },
  {
    title: 'Options',
    logged: false,
    slabs: [
      { icon: LockKeyholeOpen, target: '/me/account', text: 'Compte' },
    ],
  },
  {
    title: 'Info',
    slabs: [
      { icon: Info, target: '/me/about', text: 'A propos de Babytroc' },
      { icon: MessageCircleQuestion, target: '/me/faq', text: 'FAQ' },
      { icon: Scale, target: '/me/politics', text: 'Politiques' },
      { icon: AtSign, target: '/me/contact', text: 'Contact' },
    ],
  },
].filter(sec => sec.logged == null || unref(loggedIn) === sec.logged))
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <UserRound
        :size="32"
        :stroke-width="2"
      />
      <h1>Mes activités & options</h1>
    </template>

    <!-- Main content -->
    <main>
      <Panel>
        <PanelBanner style="font-size: 4rem; font-family: 'Plus Jakarta Sans'; font-weight: 200;">
          Babytroc
        </PanelBanner>
        <section
          v-for="section in sections"
          :key="section.title"
        >
          <h2>{{ section.title }}</h2>
          <SlabList light>
            <Slab
              v-for="slab in section.slabs"
              :key="slab.text"
              :icon="slab.icon"
              :target="slab.target"
              chevron
            >
              {{ slab.text }}
            </Slab>
          </SlabList>
        </section>
      </Panel>
    </main>
  </AppPage>
</template>
