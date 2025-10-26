<script setup lang="ts">
import { LockKeyhole } from 'lucide-vue-next'

const { data: me } = useMeQuery()
const { logout: _logout, isLoading } = useLogout()
const { $toast } = useNuxtApp()

async function logout() {
  // logout request
  try {
    await _logout()
  }
  catch {
    $toast.error('Une erreur s\'est produite')
  }
}
</script>

<template>
  <Panel class="AccountLoginPanel">
    <!-- Banner -->
    <PanelBanner :icon="LockKeyhole">
      Connecté en tant que {{ me?.email }}
    </PanelBanner>

    <TextButton
      aspect="outline"
      size="large"
      :loading="isLoading"
      :disabled="isLoading"
      @click="logout"
    >
      Se déconnecter
    </TextButton>
  </Panel>
</template>

<style scoped lang="scss">
</style>
