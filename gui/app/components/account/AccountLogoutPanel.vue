<script setup lang="ts">
import { LockKeyhole } from "lucide-vue-next";

const { data: me } = useMeQuery();
const { logout: _logout, isLoading } = useLogout();
const { $toast } = useNuxtApp();

async function logout() {
	try {
		await _logout();
	} catch {
		$toast.error("Une erreur s'est produite");
	}
}

// Password reset
const email = computed(() => me.value?.email ?? "");
const {
	askPasswordReset,
	isLoading: resetIsLoading,
	status: resetStatus,
} = useAskPasswordReset(email, "");

async function requestPasswordReset() {
	try {
		await askPasswordReset();
		$toast.success("Email de réinitialisation envoyé");
	} catch {
		$toast.error("Échec de l'envoi");
	}
}
</script>

<template>
  <Panel class="AccountLogoutPanel">
    <!-- Banner -->
    <PanelBanner :icon="LockKeyhole">
      Connecté en tant que {{ me?.email }}
    </PanelBanner>

    <div class="actions">
      <TextButton
        aspect="outline"
        size="large"
        :loading="resetIsLoading"
        :disabled="resetIsLoading || resetStatus === 'success'"
        @click="requestPasswordReset"
      >
        <template v-if="resetStatus === 'success'">
          Email envoyé
        </template>
        <template v-else>
          Modifier le mot de passe
        </template>
      </TextButton>

      <TextButton
        aspect="outline"
        size="large"
        color="red"
        :loading="isLoading"
        :disabled="isLoading"
        @click="logout"
      >
        Se déconnecter
      </TextButton>
    </div>
  </Panel>
</template>

<style scoped lang="scss">
.actions {
  display: flex;
  flex-direction: column;
  gap: $space-3;
}
</style>
