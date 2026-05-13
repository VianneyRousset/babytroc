<script setup lang="ts">
import { Box, LogIn, LogOut, Settings } from "lucide-vue-next";

const props = withDefaults(
	defineProps<{
		compact?: boolean;
	}>(),
	{
		compact: false,
	},
);

const { compact } = toRefs(props);

const { loggedIn } = useAuth();

const { me } = useMe();
const { logout } = useLogout();
const open = ref(false);
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
        <div v-if="!compact">
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
  @include font-inter;
  gap: $space-2;
  font-size: 0.9rem;
  font-weight: 500;
  color: $text-secondary;
  padding: $space-1 $space-3;

  cursor: pointer;
  transition: background 150ms ease-out;

  @include hover-only {
    background: $bg-page;
  }

  @include touch-feedback;

  &[open=true] {
    background: $bg-page;
  }
}
</style>
