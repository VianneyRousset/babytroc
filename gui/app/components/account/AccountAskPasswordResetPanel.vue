<script setup lang="ts">
import { Check, KeyRound, OctagonAlert } from "lucide-vue-next";
import type { FetchError } from "ofetch";

const emit = defineEmits(["done"]);

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const email = ref("");
const capToken = ref("");
const website = ref("");
const capResetSignal = ref(0);

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

const {
	askPasswordReset,
	isLoading,
	status,
	validationStatus,
	validationError,
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
		unref(validationStatus) === "success" &&
		unref(capToken) !== "" &&
		unref(website) === "" &&
		unref(capConfigured),
);

async function go() {
	if (!unref(canSubmit)) return;

	try {
		await askPasswordReset();
		emit("done");
	} catch (err) {
		mapErrorToToast(err as FetchError);
		capToken.value = "";
		capResetSignal.value += 1;
	}
}
</script>

<template>
  <Panel class="AccountAskPasswordReset">
    <!-- Banner -->
    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <!-- Success -->
      <PanelBanner
        v-if="status === 'success'"
        color="primary"
        :icon="Check"
      >
        Demande envoyée. Un email vous a été envoyé.
      </PanelBanner>

      <!-- Error -->
      <PanelBanner
        v-else-if="status === 'error'"
        color="red"
        :icon="OctagonAlert"
      >
        Une erreur est survenue
      </PanelBanner>

      <!-- Idle (logged out) -->
      <PanelBanner
        v-else
        :icon="KeyRound"
      />
    </transition>

    <!-- Form -->
    <h2>Vous avez oublié votre mot de passe?</h2>
    <p>Pas de soucis, on ne vous en veut pas. Entrez ici votre adresse email et nous vous enverrons un courriel pour le réinitialiser.</p>
    <WithDropdownMessage
      :status="validationStatus"
      :msg-error="validationError"
      msg-placement="top"
    >
      <TextInput
        v-model="email"
        type="email"
        placeholder="Email"
        :tabindex="1"
        autofocus
        :status="validationStatus"
        :disabled="isLoading || status === 'success'"
        @keyup.enter="go"
      />
    </WithDropdownMessage>

    <Honeypot v-model="website" />

    <CapWidget
      v-if="capConfigured"
      :api-url="cap.apiUrl"
      :site-key="cap.siteKey"
      :reset-signal="capResetSignal"
      :disabled="isLoading"
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

    <TextButton
      aspect="flat"
      size="large"
      color="neutral"
      :loading="isLoading"
      :disabled="!canSubmit || isLoading || status === 'success'"
      @click="go"
    >
      Réinitialiser
    </TextButton>
  </Panel>
</template>

<style scoped lang="scss">
.AccountAskPasswordResetPanel {
}
</style>
