<script setup lang="ts">
import {
  Plus,
  Search,
  Heart,
  MessageSquare,
  UserRound,
} from 'lucide-vue-next'
import type { FunctionalComponent } from 'vue'

const { appSectionUrls, activeAppSection } = useNavigation()

const { hot } = useChats()
const { loggedIn } = useAuth()

type ClassSpecifications = {
  section: AppSection
  target?: string
  name?: string
  icon?: FunctionalComponent
  badge?: boolean
  classes?: Record<string, boolean>
  iconSize?: number
}

const tabs = computed<Array<ClassSpecifications>>(() => [
  { section: 'explore', name: 'Explorer', icon: Search },
  { section: 'saved', name: 'Favorits', icon: Heart },
  { section: 'newitem', target: '/me/items/new', icon: Plus, classes: { plus: true, enabled: unref(loggedIn) === true }, iconSize: 53 },
  { section: 'chats', icon: MessageSquare, name: 'Chats', badge: unref(hot) },
  { section: 'me', icon: UserRound, name: 'Moi' },
])
</script>

<template>
  <nav class="AppNavigationMobile">
    <NuxtLink
      v-for="{ section, target, name, icon, badge, classes, iconSize } in tabs"
      :key="`${section}-${name}`"
      :active="activeAppSection === section"
      :class="classes ?? {}"
      :to="target ? target : appSectionUrls.get(section)"
      role="button"
      tabindex="100"
    >
      <div class="icon">
        <transition
          name="pop"
          mode="in-out"
          appear
        >
          <div
            v-if="badge ?? false"
            class="badge"
          />
        </transition>
        <component
          :is="icon"
          :size="iconSize ?? 24"
          :stroke-width="activeAppSection === section ? 2 : 1.33"
        />
      </div>
      <div v-if="name">
        {{ name }}
      </div>
    </NuxtLink>
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

  svg {
    stroke: $neutral-400;
  }

  *[active="true"] {
    color: $primary-500;
    font-weight: 700;

    svg {
      stroke: $primary-500;
    }
  }

  @include reset-list;
  @include flex-row;
  @include font-jakarta;
  justify-content: space-evenly;
  font-size: 14px;
  background: $neutral-50;
  border-top: 1px solid $neutral-300;
  color: $neutral-400;
  height: 64px;

  a {
    @include flex-column;
    @include reset-link;
    align-items: center;
    justify-content: center;
    margin: 0;
    width: 20%;
    gap: 2px;

    &.plus {
      background: $neutral-200;
      border: 2px solid $neutral-300;

      width: 64px;
      height: 64px;
      border-radius: 50%;
      position: relative;
      bottom: 20px;

      svg {
        stroke: $neutral-300;
        transform: translate(0, 1px);
      }

      &.enabled {
        background: $primary-200;
        border-color: $primary-300;

        svg {
          stroke: $primary-300;
        }

        &[active="true"] {
          color: $primary-300;
          font-weight: 400;
          background: $primary-300;
          border-color: $primary-400;

          box-shadow: 0 0 16px $primary-300;

          svg {
            stroke: $primary-50;
          }
        }
      }
    }

    .icon {
      position: relative;
    }

    .badge {
      @include flex-column-center;
      position: absolute;
      right: -0.8rem;
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
</style>
