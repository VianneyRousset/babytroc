<script setup lang="ts">
import { LockKeyhole, OctagonAlert } from "lucide-vue-next";
import type { FetchError } from "ofetch";

const { data: me } = useMeQuery();
const { logout: _logout, isLoading } = useLogout();
const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

async function logout() {
	try {
		await _logout();
	} catch {
		$toast.error("Une erreur s'est produite");
	}
}

// Password reset
const email = computed(() => me.value?.email ?? "");
const capToken = ref("");
const website = ref("");
const capResetSignal = ref(0);

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

const {
	askPasswordReset,
	isLoading: resetIsLoading,
	status: resetStatus,
} = useAskPasswordReset(email, capToken);

function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) {
		$toast.error("Captcha invalide, veuillez réessayer.");
	} else if (code === 422) {
		$toast.error("Champs invalides.");
	} else if (code === 429) {
		$toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	} else if (typeof code === "number" && code >= 500) {
		$toast.error("Erreur serveur. Réessayez plus tard.");
	} else {
		$toast.error("Problème de connexion. Vérifiez votre réseau.");
	}
}

const canSubmit = computed<boolean>(
	() =>
		capToken.value !== "" &&
		website.value === "" &&
		capConfigured.value &&
		resetStatus.value !== "success",
);

async function requestPasswordReset() {
	if (!unref(canSubmit)) return;

	try {
		await askPasswordReset();
		$toast.success("Email de réinitialisation envoyé");
	} catch (err) {
		mapErrorToToast(err as FetchError);
		capToken.value = "";
		capResetSignal.value += 1;
	}
}
</script>

<template>
  <Panel class="AccountLogoutPanel">
    <!-- Banner -->
    <PanelBanner :icon="LockKeyhole">
      Connecté en tant que {{ me?.email }}
    </PanelBanner>

    <template v-if="resetStatus !== 'success'">
      <Honeypot v-model="website" />

      <CapWidget
        v-if="capConfigured"
        :api-url="cap.apiUrl"
        :site-key="cap.siteKey"
        :reset-signal="capResetSignal"
        :disabled="resetIsLoading"
        @solve="capToken = $event"
        @expire="capToken = ''"
      />
      <PanelBanner
        v-else
        color="red"
        :icon="OctagonAlert"
      >
        Captcha indisponible.
      </PanelBanner>
    </template>

    <div class="actions">
      <TextButton
        aspect="outline"
        size="large"
        :loading="resetIsLoading"
        :disabled="!canSubmit || resetIsLoading"
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
