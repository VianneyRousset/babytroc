<script setup lang="ts">
import { OctagonAlert, X } from "lucide-vue-next";
import type { FetchError } from "ofetch";

definePageMeta({
	layout: "empty",
	appBack: true,
});

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const capToken = ref("");
const website = ref("");
const capResetSignal = ref(0);

const { mutateAsync: create, isLoading } = useCreateItemMutation();

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

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

async function submit(data: ItemFormData) {
	if (
		unref(capToken) === "" ||
		unref(website) !== "" ||
		!unref(capConfigured)
	) {
		return;
	}
	try {
		await create({
			...data,
			cap_token: unref(capToken),
			website: "",
		});
		await navigateTo("/me/items");
	} catch (err) {
		mapErrorToToast(err as FetchError);
		capToken.value = "";
		capResetSignal.value += 1;
	}
}
</script>

<template>
  <AppPage
    logged-in-only
    with-header
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack
        :icon="X"
      />
      <h1>Nouvel objet</h1>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
    </template>

    <main>
      <Panel :max-width="600">
        <ItemEditionForm
          :is-loading="isLoading"
          :submit-disabled="capToken === '' || !capConfigured"
          @submit="submit"
        />

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
          Captcha indisponible. Création désactivée.
        </PanelBanner>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
