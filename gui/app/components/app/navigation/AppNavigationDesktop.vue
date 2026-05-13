<script setup lang="ts">
const { appSectionUrls, activeAppSection } = useNavigation();

const { hot } = useChats();

const { narrowWindow } = useNarrowWindow();

type ClassSpecifications = {
	section: AppSection;
	name?: string;
	badge?: boolean;
	class?: Record<string, boolean>;
};

const tabs = computed<Array<ClassSpecifications>>(() => [
	{ section: "explore", name: "Explorer" },
	{ section: "saved", name: "Favorits" },
	{ section: "chats", name: "Chats", badge: unref(hot) },
]);
</script>

<template>
  <nav class="AppNavigationDesktop">
    <div>
      <NuxtLink
        class="logo"
        to="/"
      >
        Babytroc
      </NuxtLink>
      <ul>
        <li
          v-for="tab in tabs"
          :key="tab.section"
          :active="activeAppSection === tab.section"
          :class="tab?.class ?? {}"
          role="button"
          tabindex="100"
          @click="() => navigateTo(appSectionUrls.get(tab.section))"
        >
          <transition
            name="pop"
            mode="in-out"
            appear
          >
            <div
              v-if="tab.badge ?? false"
              class="badge"
            />
          </transition>
          <div v-if="tab.name">
            {{ tab.name }}
          </div>
        </li>
      </ul>
    </div>
    <AccountMenu :compact="narrowWindow" />
  </nav>
</template>

<style scoped lang="scss">
nav {
  @include flex-row;
  justify-content: space-between;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 14px;
  color: $text-secondary;
  background: $bg-surface;
  border-bottom: 1px solid $divider;
  padding: 0 $space-6;

  *[active="true"] {
    font-weight: 600;
    color: $text-primary;
  }

  & > div {
    @include flex-row;
    justify-content: space-between;
    padding: 0 $space-4;
    gap: $space-12;
  }

  .logo {
    @include reset-link;
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700;
    font-size: 1.25rem;
    color: $text-primary;
    letter-spacing: -0.02em;
  }

  ul {
    @include reset-list;
    @include flex-row;
    gap: $space-8;
    justify-content: space-evenly;
    height: 56px;

    li {
      position: relative;
      cursor: pointer;
      padding: $space-2 $space-3;
      border-radius: $radius-sm;
      transition: background 150ms ease-out;

      @include hover-only {
        background: $bg-page;
      }

      @include touch-feedback;

      &[active="true"] {
        background: $bg-page;
      }

      .badge {
        position: absolute;
        right: -4px;
        top: -2px;
        background: $red-600;
        min-height: 8px;
        min-width: 8px;
        border-radius: 50%;
      }
    }
  }
}
</style>
