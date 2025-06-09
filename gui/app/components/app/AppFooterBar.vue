<script setup lang="ts">
import {
  Plus,
  House,
  Bookmark,
  MessageSquare,
  UserRound,
} from 'lucide-vue-next'

const route = useRoute()

const { loggedIn } = useAuth()

const { hasNewMessages } = useChats()
</script>

<template>
  <nav>
    <ul>
      <li :active="route.path.startsWith('/home')">
        <NuxtLink to="/home">
          <div>
            <House
              :size="24"
              :stroke-width="route.path.startsWith('/home') ? 2 : 1.33"
            />
            <div>Accueil</div>
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/saved')">
        <NuxtLink
          active
          to="/saved"
        >
          <div>
            <Bookmark
              :size="24"
              :stroke-width="route.path.startsWith('/saved') ? 2 : 1.33"
            />
            <div>Sauvés</div>
          </div>
        </NuxtLink>
      </li>

      <li>
        <NuxtLink
          :to="loggedIn === true ? '/newitem' : undefined"
        >
          <div
            class="plus"
            :class="{ enable: loggedIn === true }"
          >
            <Plus
              :size="44"
              :stroke-width="2"
            />
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/chats')">
        <NuxtLink to="/chats">
          <div class="badge-container">
            <MessageSquare
              :size="24"
              :stroke-width="route.path.startsWith('/chats') ? 2 : 1.33"
            />
            <div>Chats</div>
            <transition
              name="pop"
              mode="in-out"
              appear
            >
              <div
                v-if="hasNewMessages"
                class="badge"
              />
            </transition>
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/me')">
        <NuxtLink to="/me">
          <div>
            <UserRound
              :size="24"
              :stroke-width="route.path.startsWith('/me') ? 2 : 1.33"
            />
            <div>Moi</div>
          </div>
        </NuxtLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped lang="scss">
nav {

  @include bar-shadow;

  position: fixed;
  bottom: 0px;
  box-sizing: border-box;
  z-index: 10;
  width: 100%;

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

      &[active="true"] {
        color: $primary-500;

        a {
          font-weight: 700;
        }

        svg {
          stroke: $primary-500;
        }
      }

      svg {
        stroke: $neutral-400;
      }

      a {
        @include reset-link;
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
</style>
