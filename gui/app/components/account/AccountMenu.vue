<script setup lang="ts">
import { Box, LogOut, LogIn, Settings, Ellipsis } from 'lucide-vue-next'

const { loggedIn } = useAuth()

const { me } = useMe()
const { logout } = useLogout()
const open = ref(false)

provide('dropdown-menu-open', open)
</script>

<template>
  <DropdownMenu
    v-model="open"
  >
    <template #trigger>
      <div
        v-if="loggedIn === true && me"
        class="AccountMenuTrigger"
        :open="open"
      >
        <UserAvatar
          :seed="me.avatar_seed"
          :size="48"
        />
        <div>
          {{ me.name }}
        </div>
      </div>
      <Ellipsis
        v-else
        class="AccountMenuTrigger"
        :size="32"
        :stroke-width="1.5"
      />
    </template>
    <DropdownItem
      v-if="loggedIn === true"
      :icon="Box"
      target="/me/items"
    >
      Mes Objets
    </DropdownItem>
    <DropdownItem
      :icon="Settings"
      target="/me"
    >
      Options et info
    </DropdownItem>
    <DropdownItem
      v-if="loggedIn === true"
      :icon="LogOut"
      red
      @click="logout"
    >
      Se déconnecter
    </DropdownItem>
    <DropdownItem
      v-else
      :icon="LogIn"
      target="/me/account"
    >
      Se connecter
    </DropdownItem>
  </DropdownMenu>
</template>

<style scoped lang="scss">
.AccountMenuTrigger {
  @include flex-row;
  @include font-jakarta;
  gap: 0.6em;
  font-size: 1.4em;
  font-weight: 600;
  color: $neutral-600;
  padding: 2px 4px;

  border: 1px solid transparent;
  border-radius: 0.4em;
  cursor: pointer;

  &:hover {
    background: $neutral-50;
    border-color: $neutral-200;
  }

  &:active,
  &[open=true] {
    background: $neutral-100;
    border-color: $neutral-300;
  }
}
</style>
