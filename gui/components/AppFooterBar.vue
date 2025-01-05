<script setup lang="ts">

import { Plus, House, Bookmark, MessageSquare, UserRound } from 'lucide-vue-next';

const route = useRoute();

</script>

<template>
  <nav>
    <ul>

      <li :active="route.path.startsWith('/home')">
        <NuxtLink to="/home">
          <div>
            <House :size="24" :strokeWidth="route.path.startsWith('/home') ? 2 : 1.33" :absoluteStrokeWidth="true" />
            <div>Accueil</div>
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/saved')">
        <NuxtLink active to="/saved">
          <div>
            <Bookmark :size="24" :strokeWidth="route.path.startsWith('/saved') ? 2 : 1.33"
              :absoluteStrokeWidth="true" />
            <div>Sauvés</div>
          </div>
        </NuxtLink>
      </li>

      <li>
        <NuxtLink active to="/newitem">
          <div class="plus">
            <Plus :size="44" :strokeWidth="2" :absoluteStrokeWidth="true" />
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/chats')">
        <NuxtLink to="/chats">
          <div>
            <MessageSquare :size="24" :strokeWidth="route.path.startsWith('/chats') ? 2 : 1.33"
              :absoluteStrokeWidth="true" />
            <div>Chats</div>
          </div>
        </NuxtLink>
      </li>

      <li :active="route.path.startsWith('/me')">
        <NuxtLink to="/me">
          <div>
            <UserRound :size="24" :strokeWidth="route.path.startsWith('/me') ? 2 : 1.33" :absoluteStrokeWidth="true" />
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


        &.plus {

          background: $primary-200;
          border: 2px solid $primary-300;

          width: 64px;
          height: 64px;
          border-radius: 50%;
          position: relative;
          bottom: 20px;

          svg {
            stroke: $primary-300;
          }
        }
      }

    }

  }
}
</style>
