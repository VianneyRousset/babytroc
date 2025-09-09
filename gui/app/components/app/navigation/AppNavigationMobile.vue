<script setup lang="ts">
import {
  Plus,
  House,
  Heart,
  MessageSquare,
  UserRound,
} from 'lucide-vue-next'
import type { FunctionalComponent } from 'vue'

const { appSectionUrls, activeAppSection } = useNavigation()

const { hasNewMessages } = useChats()

type ClassSpecifications = {
  section: AppSection
  name?: string
  icon?: FunctionalComponent
  badge?: boolean
  class?: Record<string, boolean>
}

const tabs = computed<Array<ClassSpecifications>>(() => [
  { section: 'explore', name: 'Accueil', icon: House },
  { section: 'liked', name: 'Favorits', icon: Heart },
  { section: 'newitem', icon: Plus, class: { plus: true } },
  { section: 'chats', icon: MessageSquare, name: 'Chats', badge: unref(hasNewMessages) },
  { section: 'me', icon: UserRound, name: 'Moi' },
])
</script>

<template>
  <nav class="AppNavigationMobile">
    <ul>
      <li
        v-for="tab in tabs"
        :key="tab.section"
        :active="activeAppSection === tab.section"
        :class="tab?.class ?? {}"
      >
        <NuxtLink :to="appSectionUrls.get(tab.section)">
          <component
            :is="tab.icon"
            :size="24"
            :stroke-width="activeAppSection === tab.section ? 2 : 1.33"
          />
          <div v-if="tab.name">{{ tab.name }}</div>
          <transition
            name="pop"
            mode="in-out"
            appear
          >
            <div
              v-if="tab?.badge ?? false"
              class="badge"
            />
          </transition>
        </NuxtLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped lang="scss">
nav {

  @include bar-shadow;

  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  box-sizing: border-box;

  ul {

    @include reset-list;
    @include flex-row;
    font-family: 'Instrument Sans';
    justify-content: space-evenly;
    font-size: 14px;
    background: $neutral-50;
    border-top: 1px solid $neutral-300;
    color: $neutral-400;
    height: 64px;

    li {
      @include flex-column;
      margin: 0;
      width: 20%;

      a {
        @include reset-link;
      }

      svg {
        stroke: $neutral-400;
      }

      &[active="true"] {
        color: $primary-500;

        a {
          font-weight: 700;
        }

        svg {
          stroke: $primary-500;
        }
      }

      div {
        @include flex-column;
        justify-content: center;
        gap: 4px;
        position: relative;

        &.plus {
          background: $neutral-200;
          border: 2px solid $neutral-300;

          &.enable {
            background: $primary-200;
            border-color: $primary-300;

            svg {
              stroke: $primary-300;
            }
          }

          width: 64px;
          height: 64px;
          border-radius: 50%;
          position: relative;
          bottom: 20px;

          svg {
            stroke: $neutral-300;
          }
        }

      }

      .badge {
        @include flex-column-center;
        position: absolute;
        right: -0.5rem;
        top: -0.3rem;
        background: $primary-300;
        min-height: 0.75rem;
        min-width: 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        color: white;
      }
    }
  }
}
</style>
