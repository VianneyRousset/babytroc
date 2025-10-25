<script setup lang="ts">
import { Box, LogOut, UserRound } from 'lucide-vue-next'

const { me } = useMe()
const { logout } = useAuth()
const open = ref(false)

provide('dropdown-menu-open', open)
</script>

<template>
  <DropdownMenu
    v-if="me"
    v-model="open"
  >
    <template #trigger>
      <div
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
    </template>
    <DropdownItem
      :icon="Box"
      target="/me/items"
    >
      Mes Objets
    </DropdownItem>
    <DropdownItem
      :icon="UserRound"
      target="/me"
    >
      Mon compte
    </DropdownItem>
    <DropdownItem
      :icon="LogOut"
      red
      @click="logout"
    >
      Se déconnecter
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
