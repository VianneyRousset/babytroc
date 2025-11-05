<script setup lang="ts">
const { appSectionUrls, activeAppSection } = useNavigation()

const { hot } = useChats()

const { narrowWindow } = useNarrowWindow()

type ClassSpecifications = {
  section: AppSection
  name?: string
  badge?: boolean
  class?: Record<string, boolean>
}

const tabs = computed<Array<ClassSpecifications>>(() => [
  { section: 'explore', name: 'Explorer' },
  { section: 'liked', name: 'Favorits' },
  { section: 'chats', name: 'Chats', badge: unref(hot) },
])
</script>

<template>
  <nav class="AppNavigationDesktop">
    <div>
      <div class="logo">
        Babytroc
      </div>
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
  font-family: 'Plus Jakarta Sans';
  font-weight: 500;
  color: $neutral-500;
  border-bottom: 1px solid $neutral-200;
  padding: 0 1em;

  *[active="true"] {
    font-weight: 600;
    color: $neutral-900;
  }

  & > div {
    @include flex-row;
    justify-content: space-between;
    padding: 0 1rem;
    gap: 3rem;
  }

  ul {
    @include reset-list;
    @include flex-row;
    gap: 2rem;
    justify-content: space-evenly;
    height: 64px;

    li {
      position: relative;
      cursor: pointer;
      &:hover {
        color: $neutral-700;
      }
      .badge {
        @include flex-column-center;
        position: absolute;
        right: -0.8rem;
        top: -0.5rem;
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
