<script setup lang="ts">
import { Heart, MessageSquare, Plus, Search, UserRound } from "lucide-vue-next";
import type { FunctionalComponent } from "vue";

const { appSectionUrls, activeAppSection } = useNavigation();

const { hot } = useChats();
const { loggedIn } = useAuth();

type ClassSpecifications = {
	section: AppSection;
	target?: string;
	name?: string;
	icon?: FunctionalComponent;
	badge?: boolean;
	iconSize?: number;
};

const tabs = computed<Array<ClassSpecifications>>(() => [
	{ section: "explore", name: "Explorer", icon: Search },
	{ section: "saved", name: "Favorits", icon: Heart },
	{ section: "newitem", target: "/me/items/new", icon: Plus, iconSize: 53 },
	{ section: "chats", icon: MessageSquare, name: "Chats", badge: unref(hot) },
	{ section: "me", icon: UserRound, name: "Moi" },
]);
</script>

<template>
  <nav class="AppNavigationMobile">
    <NuxtLink
      v-for="{ section, target, name, icon, badge, iconSize } in tabs"
      :key="`${section}-${name}`"
      :active="activeAppSection === section"
      :to="target ? target : appSectionUrls.get(section)"
      :section="section"
      :logged-in="loggedIn === true"
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
          :stroke-width="activeAppSection === section ? 2 : 1.5"
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
  @include flex-row;
  @include font-inter;
  @include safe-area-bottom;
  justify-content: space-evenly;
  font-size: 10px;
  font-weight: 500;
  background: $bg-surface;
  border-top: 1px solid $divider;
  height: 64px;

  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  box-sizing: border-box;
  z-index: 5;

  a {
    @include flex-column;
    @include reset-link;
    align-items: center;
    justify-content: center;
    margin: 0;
    width: 20%;
    gap: 2px;

    color: $text-tertiary;

    @include touch-feedback;

    &[active="true"] {
      color: $text-primary;
      font-weight: 600;
    }
  }

  a[section="saved"][logged-in=false],
  a[section="chats"][logged-in=false] {
    opacity: 0.4;
  }

  a[section="newitem"] {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    position: relative;
    bottom: 20px;

    background: $neutral-200;
    border: 2px solid $neutral-300;

    svg {
      stroke: $neutral-400;
      transform: translate(0, 1px);
    }

    &[active="true"] {
      background: $neutral-300;
      border-color: $neutral-400;
      svg {
        stroke: $bg-surface;
      }
    }

    &[logged-in=true] {
      background: $primary-200;
      border-color: $primary-300;

      svg {
        stroke: $primary-text-safe;
      }

      &[active="true"] {
        background: $primary-300;
        border-color: $primary-400;

        svg {
          stroke: $primary-50;
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
      background: $red-600;
      min-height: 8px;
      min-width: 8px;
      border-radius: 50%;
    }
  }
}
</style>
