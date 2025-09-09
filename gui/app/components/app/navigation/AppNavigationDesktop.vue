<script setup lang="ts">
const { appSectionUrls, activeAppSection } = useNavigation()

const { hasNewMessages } = useChats()

const tabs = computed<Array<{ section: AppSection, name: string, badge?: boolean }>>(() => [
  { section: 'explore', name: 'Accueil' },
  { section: 'chats', name: 'Chats', badge: unref(hasNewMessages) },
  { section: 'me', name: 'Moi' },
])
</script>

<template>
  <nav>
    <ul>
      <li
        v-for="tab in tabs"
        :key="tab.section"
        :active="activeAppSection === tab.section"
      >
        <NuxtLink :to="appSectionUrls.get(tab.section)">
          <div>{{ tab.name }}</div>
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

  ul {

    @include reset-list;
    @include flex-row;
    font-family: 'Plus Jakarta Sans';
    justify-content: space-evenly;
    font-size: 14px;

    li {

      a {
        @include reset-link;
      }

      &[active="true"] {
        color: $primary-500;

        a {
          font-weight: 700;
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
